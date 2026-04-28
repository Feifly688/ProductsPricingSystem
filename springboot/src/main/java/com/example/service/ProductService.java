/**
 * ProductService
 *
 * @author Feiqi
 * @date 2025/3/13  13:23
 */
package com.example.service;

import com.example.entity.Product;
import com.example.mapper.ProductMapper;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class ProductService {
    @Resource
    private ProductMapper productMapper;

    public List<Product> selectAll(Product product) {
        return productMapper.selectAll(product);
    }

    /**
     * 分页
     *
     * @param pageNum    当前页码
     * @param pageSize   当前页面大小
     * @param sortColumn 排序列
     * @param sortOrder  排序方式(asc/desc)
     * @return 分页对象（包含数据和分页参数）
     */
    public PageInfo<Product> selectPage(Product product, Integer pageNum, Integer pageSize, String sortColumn, String sortOrder) {
        // 构建排序字符串
        String orderBy = null;
        if (sortColumn != null && !sortColumn.isEmpty() && sortOrder != null && !sortOrder.isEmpty()) {
            orderBy = sortColumn + " " + sortOrder;
        }
        
        // 使用正确的方式设置分页和排序
        if (orderBy != null) {
            PageHelper.startPage(pageNum, pageSize, orderBy);
        } else {
            PageHelper.startPage(pageNum, pageSize);
        }
        
        List<Product> list = productMapper.selectAll(product);
        return PageInfo.of(list);
    }

    /**
     * 新增
     */
    public void add(Product product) {
        productMapper.insert(product);
    }

    /**
     * 修改
     */
    public void updateById(Product product) {
        productMapper.updateById(product);
    }

    /**
     * 根据id删除
     */
    public void deleteById(Integer id) {
        productMapper.deleteById(id);
    }
}
