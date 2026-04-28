package com.example.entity;

import com.fasterxml.jackson.annotation.JsonFormat;

import java.math.BigDecimal;
import java.util.Date;
import java.util.List;

/**
 * 商品检测价格记录
 */
public class PricingRecord {
    /**
     * ID
     */
    private String id;

    /**
     * 检测后的图片路径
     */
    private String imagePath;

    /**
     * 总价格
     */
    private BigDecimal totalPrice;

    /**
     * 商品总数量
     */
    private Integer itemCount;

    /**
     * 检测用时(ms)
     */
    private Float detectionDuration;

    /**
     * 运行时长(s)
     */
    private Float executeDuration;

    /**
     * 创建时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date createTime;
    
    /**
     * 创建用户ID
     */
    private String createUserId;
    
    /**
     * 创建用户名称
     */
    private String createUserName;
    
    /**
     * 商品明细列表 (非数据库字段，用于接收前端数据)
     */
    private transient List<PricingRecordItem> items;
    
    /**
     * 商品明细JSON (非数据库字段，用于接收前端数据)
     */
    private transient String itemsJson;

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getImagePath() {
        return imagePath;
    }

    public void setImagePath(String imagePath) {
        this.imagePath = imagePath;
    }

    public BigDecimal getTotalPrice() {
        return totalPrice;
    }

    public void setTotalPrice(BigDecimal totalPrice) {
        this.totalPrice = totalPrice;
    }

    public Integer getItemCount() {
        return itemCount;
    }

    public void setItemCount(Integer itemCount) {
        this.itemCount = itemCount;
    }

    public Float getDetectionDuration() {
        return detectionDuration;
    }

    public void setDetectionDuration(Float detectionDuration) {
        this.detectionDuration = detectionDuration;
    }

    public Float getExecuteDuration() {
        return executeDuration;
    }

    public void setExecuteDuration(Float executeDuration) {
        this.executeDuration = executeDuration;
    }

    public Date getCreateTime() {
        return createTime;
    }

    public void setCreateTime(Date createTime) {
        this.createTime = createTime;
    }

    public String getCreateUserId() {
        return createUserId;
    }

    public void setCreateUserId(String createUserId) {
        this.createUserId = createUserId;
    }

    public String getCreateUserName() {
        return createUserName;
    }

    public void setCreateUserName(String createUserName) {
        this.createUserName = createUserName;
    }

    public List<PricingRecordItem> getItems() {
        return items;
    }

    public void setItems(List<PricingRecordItem> items) {
        this.items = items;
    }
    
    public String getItemsJson() {
        return itemsJson;
    }
    
    public void setItemsJson(String itemsJson) {
        this.itemsJson = itemsJson;
    }
} 