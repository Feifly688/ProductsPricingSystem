package com.example.entity;

import java.math.BigDecimal;

/**
 * 价格记录明细项
 */
public class PricingRecordItem {
    /**
     * ID
     */
    private String id;
    
    /**
     * 关联的记录ID
     */
    private String recordId;
    
    /**
     * 商品名称
     */
    private String name;
    
    /**
     * 商品数量
     */
    private Integer count;
    
    /**
     * 商品单价
     */
    private BigDecimal price;

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getRecordId() {
        return recordId;
    }

    public void setRecordId(String recordId) {
        this.recordId = recordId;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Integer getCount() {
        return count;
    }

    public void setCount(Integer count) {
        this.count = count;
    }

    public BigDecimal getPrice() {
        return price;
    }

    public void setPrice(BigDecimal price) {
        this.price = price;
    }
} 