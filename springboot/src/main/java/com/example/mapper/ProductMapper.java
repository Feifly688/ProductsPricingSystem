/**
 * ProductMapper
 *
 * @author Feiqi
 * @date 2025/3/13  13:23
 */

package com.example.mapper;

import com.example.entity.Product;
import org.apache.ibatis.annotations.Param;

import java.util.List;

public interface ProductMapper {
    /**
     * 查询所有
     */
    List<Product> selectAll(Product product);

    /**
     * 新增
     */
    void insert(Product product);

    /**
     * 修改
     */
    void updateById(Product product);

    /**
     * 删除
     */
    void deleteById(Integer id);
    
    /**
     * 修改销售量
     * @param name 商品名称
     * @param count 销售数量
     * @return 影响的行数
     */
    int updateSales(@Param("name") String name, @Param("count") int count);
    
    /**
     * 检查商品是否存在
     * @param name 商品名称
     * @return 存在的商品数量，大于0表示存在
     */
    int checkProductExists(@Param("name") String name);
}
