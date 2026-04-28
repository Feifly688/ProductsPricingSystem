/**
 * UserMapper
 *
 * @author Feiqi
 * @date 2025/1/9  15:11
 */

package com.example.mapper;

import com.example.entity.User;
import org.apache.ibatis.annotations.Select;

import java.util.List;

/**
 * 操作user相关数据接口
 */
public interface UserMapper {
    /**
     * 查询所有
     */
    List<User> selectAll(User user);

    /**
     * 根据ID查询
     */
    User selectById(Integer id);

    /**
     * 根据用户名查询
     */
    User selectByUsername(String username);

    /**
     * 根据电话号码查询
     */
    User selectByPhone(String phone);

    /**
     * 新增
     */
    void insert(User user);

    /**
     * 修改
     */
    void updateById(User user);

    /**
     * 删除
     */
    void deleteById(Integer id);
}
