package com.example.service.impl;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.example.entity.PricingRecord;
import com.example.entity.PricingRecordItem;
import com.example.mapper.PricingRecordMapper;
import com.example.service.PricingRecordService;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import jakarta.annotation.Resource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.io.File;
import java.math.BigDecimal;
import java.nio.file.Paths;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Service
public class PricingRecordServiceImpl implements PricingRecordService {

    private static final Logger logger = LoggerFactory.getLogger(PricingRecordServiceImpl.class);

    @Value("${python.script.path:}")
    private String pythonScriptPath;

    @Resource
    private PricingRecordMapper pricingRecordMapper;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void savePricingRecord(PricingRecord record) {
        // 生成唯一ID
        String recordId = UUID.randomUUID().toString().replace("-", "");
        record.setId(recordId);

        // 处理商品明细（修复Double精度丢失）
        List<PricingRecordItem> items = parseRecordItems(record.getItemsJson(), recordId);
        record.setItems(items);
        record.setItemCount(items.size());

        // 保存主记录
        logger.info("保存计价主记录: ID={}, 总价={}, 商品数量={}", recordId, record.getTotalPrice(), items.size());
        pricingRecordMapper.insertRecord(record);

        // 批量保存明细
        if (!items.isEmpty()) {
            pricingRecordMapper.batchInsertRecordItems(items);
            logger.info("批量保存{}条商品明细完成", items.size());
        }
    }

    @Override
    public PageInfo<PricingRecord> getPricingRecordsByPage(Integer pageNum, Integer pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<PricingRecord> records = pricingRecordMapper.selectAllRecords();
        return new PageInfo<>(records);
    }

    @Override
    public PageInfo<PricingRecord> getPricingRecordsByUserId(String userId, Integer pageNum, Integer pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<PricingRecord> records = pricingRecordMapper.selectRecordsByUserId(userId);
        return new PageInfo<>(records);
    }

    @Override
    public PricingRecord getPricingRecordById(String id) {
        return StringUtils.hasText(id) ? pricingRecordMapper.selectRecordById(id) : null;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean deleteRecordAndItems(String id) {
        if (!StringUtils.hasText(id)) {
            logger.warn("删除计价记录失败：ID为空");
            return false;
        }

        // 校验记录存在性
        PricingRecord record = pricingRecordMapper.selectRecordById(id);
        if (record == null) {
            logger.warn("删除计价记录失败：ID={} 的记录不存在", id);
            return false;
        }

        // 删除关联的图片文件（results/images 目录下）
        deleteImageFileIfPresent(record.getImagePath());

        // 先删明细（外键约束），再删主记录
        pricingRecordMapper.deleteRecordItemsByRecordId(id);
        int deleteCount = pricingRecordMapper.deleteRecordById(id);
        return deleteCount > 0;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public int batchDeleteRecords(List<String> ids) {
        if (ids == null || ids.isEmpty()) {
            logger.warn("批量删除失败：ID列表为空");
            return 0;
        }

        // 先删除每条记录关联的图片文件，再删库
        for (String id : ids) {
            PricingRecord record = pricingRecordMapper.selectRecordById(id);
            if (record != null) {
                deleteImageFileIfPresent(record.getImagePath());
            }
        }

        // 批量删除明细与主记录
        pricingRecordMapper.batchDeleteRecordItems(ids);
        int deleteCount = pricingRecordMapper.batchDeleteRecords(ids);
        logger.info("批量删除完成，成功删除{}条记录", deleteCount);
        return deleteCount;
    }

    /**
     * 若 image_path 指向 results/images 下的文件，则删除该文件（与 yolov8 results/images 目录一致）
     */
    private void deleteImageFileIfPresent(String imagePath) {
        if (!StringUtils.hasText(imagePath) || !imagePath.contains("results/images")) {
            return;
        }
        if (pythonScriptPath == null || pythonScriptPath.isEmpty()) {
            return;
        }
        String fileName = imagePath.substring(imagePath.lastIndexOf('/') + 1);
        if (fileName.isEmpty()) {
            return;
        }
        try {
            File file = Paths.get(pythonScriptPath).getParent().resolve("results").resolve("images").resolve(fileName).toFile();
            if (file.exists() && file.isFile()) {
                if (file.delete()) {
                    logger.info("已删除计价记录关联图片: {}", file.getAbsolutePath());
                } else {
                    logger.warn("删除图片失败: {}", file.getAbsolutePath());
                }
            }
        } catch (Exception e) {
            logger.warn("删除计价记录关联图片时出错，忽略: {}", e.getMessage());
        }
    }

    // 抽取明细解析逻辑，减少冗余
    private List<PricingRecordItem> parseRecordItems(String itemsJson, String recordId) {
        List<PricingRecordItem> items = new ArrayList<>();
        if (!StringUtils.hasText(itemsJson)) {
            return items;
        }

        try {
            JSONArray jsonArray = JSON.parseArray(itemsJson);
            logger.info("解析商品数据，共{}条", jsonArray.size());

            for (int i = 0; i < jsonArray.size(); i++) {
                JSONObject item = jsonArray.getJSONObject(i);
                PricingRecordItem recordItem = new PricingRecordItem();
                recordItem.setId(UUID.randomUUID().toString().replace("-", ""));
                recordItem.setRecordId(recordId);
                recordItem.setName(item.getString("name"));
                recordItem.setCount(item.getInteger("count"));

                // 修复Double转BigDecimal精度丢失
                String priceStr = item.getString("price");
                recordItem.setPrice(StringUtils.hasText(priceStr)
                        ? new BigDecimal(priceStr).setScale(2, RoundingMode.HALF_UP)
                        : BigDecimal.ZERO);

                items.add(recordItem);
                logger.info("商品项 #{}: 名称={}, 数量={}, 单价={}", i + 1, recordItem.getName(), recordItem.getCount(), recordItem.getPrice());
            }
        } catch (Exception e) {
            logger.error("处理商品数据失败", e);
            throw new RuntimeException("处理商品数据失败: " + e.getMessage(), e);
        }
        return items;
    }
}
