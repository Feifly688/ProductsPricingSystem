package com.example.service;

import com.example.mapper.DetectMapper;
import com.example.mapper.ProductMapper;
import jakarta.annotation.Resource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Map;

@Service
public class DetectService {
    private static final Logger logger = LoggerFactory.getLogger(DetectService.class);
    
    @Resource
    private DetectMapper detectMapper;

    @Resource
    private ProductMapper productMapper;
    
    public Map<String, Object> getPriceData() {
        return detectMapper.getPriceData();
    }

    @Transactional
    public void updateProductSales(String name, int count){
        logger.info("开始更新商品销售量：商品={}, 数量={}", name, count);
        // 查询商品是否存在
        int productExists = productMapper.checkProductExists(name);
        logger.info("商品{}存在检查结果：{}", name, productExists > 0 ? "存在" : "不存在");
        
        if (productExists > 0) {
            int rows = productMapper.updateSales(name, count);
            logger.info("更新商品{}销售量结果：更新了{}行", name, rows);
        } else {
            logger.warn("商品{}不存在，无法更新销售量", name);
        }
    }
}
