package com.example.service;

import com.example.entity.PricingRecord;
import com.github.pagehelper.PageInfo;

import java.util.List;

public interface PricingRecordService {

    /**
     * 保存检测记录
     * @param record 检测记录
     */
    void savePricingRecord(PricingRecord record);

    /**
     * 获取所有检测记录（分页）
     * @param pageNum 页码
     * @param pageSize 页大小
     * @return 分页检测记录列表
     */
    PageInfo<PricingRecord> getPricingRecordsByPage(Integer pageNum, Integer pageSize);

    /**
     * 获取指定用户的检测记录（分页）
     * @param userId 用户ID
     * @param pageNum 页码
     * @param pageSize 页大小
     * @return 分页检测记录列表
     */
    PageInfo<PricingRecord> getPricingRecordsByUserId(String userId, Integer pageNum, Integer pageSize);

    /**
     * 根据ID查询单条记录
     * @param id 记录ID
     * @return 计价记录
     */
    PricingRecord getPricingRecordById(String id);

    /**
     * 删除计价记录（主表+关联明细）
     * @param id 记录ID
     * @return 是否删除成功
     */
    boolean deleteRecordAndItems(String id);

    /**
     * 批量删除计价记录
     * @param ids 记录ID列表
     * @return 成功删除数量
     */
    int batchDeleteRecords(List<String> ids);
}
