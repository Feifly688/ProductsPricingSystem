/**
 * ProductController
 *
 * @author Feiqi
 * @date 2025/3/13  13:19
 */
package com.example.controller;

import com.example.common.Result;
import com.example.entity.Product;
import com.example.service.ProductService;
import com.github.pagehelper.PageInfo;
import jakarta.annotation.Resource;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.HashMap;

@RestController
@RequestMapping("/product")
public class ProductController {

    @Resource
    private ProductService productService;

    /**
     * 查询所有
     */
    @GetMapping("/selectAll")
    public Result selectAll(Product product) {
        List<Product> list = productService.selectAll(product);
        return Result.success(list);
    }

    /**
     * 分页模糊查询
     */
    @GetMapping("/selectPage")
    public Result selectPage(Product product,
                             @RequestParam(defaultValue = "1") Integer pageNum, 
                             @RequestParam(defaultValue = "10") Integer pageSize,
                             @RequestParam(required = false) String sortColumn,
                             @RequestParam(required = false) String sortOrder) {
        PageInfo<Product> pageInfo = productService.selectPage(product, pageNum, pageSize, sortColumn, sortOrder);
        return Result.success(pageInfo);
    }
    /**
     * 新增
     */
    @PostMapping("/add")
    public Result add(@RequestBody Product product) {
        productService.add(product);
        return Result.success();
    }

    /**
     * 更新
     *
     * @param product
     * @return
     */
    @PutMapping("/update")
    public Result update(@RequestBody Product product) {
        productService.updateById(product);
        return Result.success();
    }

    /**
     * @param id
     * @return
     */
    @DeleteMapping("/delete/{id}")
    public Result deleteById(@PathVariable Integer id) {
        productService.deleteById(id);
        return Result.success();
    }

    /**
     * 获取所有商品的销售量数据
     */
    @GetMapping("/sales")
    public Result getSalesData() {
        List<Product> products = productService.selectAll(new Product());
        return Result.success(products.stream()
                .map(p -> {
                    Product result = new Product();
                    result.setName(p.getName());
                    result.setSales(p.getSales());
                    return result;
                })
                .filter(p -> p.getSales() > 0)
                .toList());
    }

    /**
     * 获取按类别统计的销售数据
     */
    @GetMapping("/sales/category")
    public Result getSalesByCategory() {
        List<Product> products = productService.selectAll(new Product());
        
        // 定义商品类别
        String[] categories = {"饮料类", "零食类", "方便食品", "日用品", "文具类", "个人护理", 
                               "糖果巧克力", "坚果炒货", "烘焙食品", "其他商品"};
        
        // 按类别分组并统计销量
        Map<String, Integer> categorySales = new HashMap<>();
        
        // 初始化类别
        for (String category : categories) {
            categorySales.put(category, 0);
        }
        
        for (Product product : products) {
            if (product.getName() == null || product.getSales() == 0) {
                continue;
            }
            
            // 根据商品名称分配到对应类别
            String category = "其他商品";
            String name = product.getName().toLowerCase();
            
            if (name.contains("可乐") || name.contains("饮料") || name.contains("水") || name.contains("茶")) {
                category = "饮料类";
            } else if (name.contains("薯片") || name.contains("零食") || name.contains("小吃")) {
                category = "零食类";
            } else if (name.contains("面") || name.contains("饭") || name.contains("米") || name.contains("快餐")) {
                category = "方便食品";
            } else if (name.contains("纸") || name.contains("巾") || name.contains("洗") || name.contains("清洁")) {
                category = "日用品";
            } else if (name.contains("笔") || name.contains("本") || name.contains("纸张")) {
                category = "文具类";
            } else if (name.contains("护肤") || name.contains("洗发") || name.contains("牙膏")) {
                category = "个人护理";
            } else if (name.contains("糖") || name.contains("巧克力")) {
                category = "糖果巧克力";
            } else if (name.contains("坚果") || name.contains("瓜子") || name.contains("花生")) {
                category = "坚果炒货";
            } else if (name.contains("蛋糕") || name.contains("面包") || name.contains("饼干")) {
                category = "烘焙食品";
            }
            
            Integer sales = product.getSales();
            categorySales.put(category, categorySales.getOrDefault(category, 0) + sales);
        }
        
        // 转换为前端需要的格式
        List<Map<String, Object>> result = categorySales.entrySet().stream()
                .filter(entry -> entry.getValue() > 0)
                .map(entry -> {
                    Map<String, Object> item = new HashMap<>();
                    item.put("name", entry.getKey());
                    item.put("value", entry.getValue());
                    return item;
                })
                .toList();
        
        return Result.success(result);
    }
}
