/**
 * AdminMapper
 *
 * @author Feiqi
 * @date 2025/1/6  18:22
 */

package com.example.mapper;

import com.example.entity.Admin;

import java.util.List;

/**
 * 操作admin相关数据接口
 */
public interface AdminMapper {
    /**
     * 查询所有
     */
    List<Admin> selectAll(Admin admin);

    /**
     * 根据ID查询
     */
    Admin selectById(Integer id);

    /**
     * 根据用户名查询
     */
    Admin selectByUsername(String username);

    /**
     * 新增
     */
    void insert(Admin admin);

    /**
     * 修改
     */
    void updateById(Admin admin);

    /**
     * 删除
     */
    void deleteById(Integer id);
}
