package com.example.controller;

import com.example.common.Result;
import com.example.entity.Account;
import com.example.entity.PricingRecord;
import com.example.service.PricingRecordService;
import com.github.pagehelper.PageInfo;
import jakarta.annotation.Resource;
import jakarta.servlet.http.HttpServletRequest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.util.StringUtils; // 关键导入
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.Date;
import java.util.List;

@RestController
@RequestMapping("/pricingRecord")
public class PricingRecordController {
    private static final Logger logger = LoggerFactory.getLogger(PricingRecordController.class);

    @Resource
    private PricingRecordService pricingRecordService;

    /**
     * 保存价格检测记录
     */
    @PostMapping
    public Result save(@RequestBody PricingRecord record, HttpServletRequest request) {
        logger.info("保存价格记录: {}", record);
        try {
            // 基础校验
            if (record == null) {
                return Result.error("记录数据不能为空");
            }

            // 补全默认值
            if (record.getCreateTime() == null) record.setCreateTime(new Date());
            if (record.getTotalPrice() == null) record.setTotalPrice(BigDecimal.ZERO);
            // image_path 为 varchar(255)，禁止写入 base64 或超长字符串
            String rawPath = record.getImagePath();
            if (rawPath != null && (rawPath.startsWith("data:") || rawPath.length() > 255)) {
                record.setImagePath("/images/detection.jpg");
            }

            // 绑定操作用户
            Account user = (Account) request.getSession().getAttribute("user");
            if (user != null) {
                record.setCreateUserId(String.valueOf(user.getId()));
                record.setCreateUserName(user.getName());
            } else {
                logger.warn("保存价格记录时未获取到登录用户，忽略用户信息");
            }

            pricingRecordService.savePricingRecord(record);
            return Result.success(record.getId());
        } catch (Exception e) {
            logger.error("保存价格记录失败", e);
            return Result.error("保存失败: " + e.getMessage());
        }
    }

    /**
     * 分页获取价格检测记录
     */
    @GetMapping("/page")
    public Result getByPage(
            @RequestParam(defaultValue = "1") Integer pageNum,
            @RequestParam(defaultValue = "10") Integer pageSize) {
        logger.info("分页获取价格记录，页码：{}，页大小：{}", pageNum, pageSize);
        try {
            PageInfo<PricingRecord> pageInfo = pricingRecordService.getPricingRecordsByPage(pageNum, pageSize);
            return Result.success(pageInfo);
        } catch (Exception e) {
            logger.error("分页获取价格记录失败", e);
            return Result.error("获取失败: " + e.getMessage());
        }
    }

    /**
     * 根据ID查询单条记录
     */
    @GetMapping("/{id}")
    public Result getById(@PathVariable String id) {
        logger.info("查询价格记录，ID：{}", id);
        try {
            if (!StringUtils.hasText(id)) { // 使用StringUtils校验
                return Result.error("记录ID不能为空");
            }
            PricingRecord record = pricingRecordService.getPricingRecordById(id);
            return record != null ? Result.success(record) : Result.error("记录不存在");
        } catch (Exception e) {
            logger.error("查询价格记录失败，ID：{}", id, e);
            return Result.error("查询失败：" + e.getMessage());
        }
    }

    /**
     * 删除计价记录（主表+关联表）
     */
    @DeleteMapping("/{id}")
    public Result deletePricingRecord(@PathVariable String id) {
        try {
            if (!StringUtils.hasText(id)) { // 使用StringUtils校验
                return Result.error("记录ID不能为空");
            }
            boolean success = pricingRecordService.deleteRecordAndItems(id);
            return success ? Result.success("删除成功") : Result.error("删除失败，记录不存在");
        } catch (Exception e) {
            logger.error("删除计价记录失败，ID: {}", id, e);
            return Result.error("删除失败：" + e.getMessage());
        }
    }

    /**
     * 批量删除计价记录
     */
    @DeleteMapping("/batch")
    public Result batchDelete(@RequestBody List<String> ids) {
        logger.info("批量删除计价记录，ID列表：{}", ids);
        try {
            if (ids == null || ids.isEmpty()) {
                return Result.error("待删除ID列表不能为空");
            }
            int deleteCount = pricingRecordService.batchDeleteRecords(ids);
            return Result.success("成功删除 " + deleteCount + " 条记录");
        } catch (Exception e) {
            logger.error("批量删除计价记录失败", e);
            return Result.error("批量删除失败：" + e.getMessage());
        }
    }
}
