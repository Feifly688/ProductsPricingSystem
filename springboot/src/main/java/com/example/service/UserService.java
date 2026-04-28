/**
 * UserService
 *
 * @author Feiqi
 * @date 2025/1/9  15:07
 */
package com.example.service;

import cn.hutool.core.util.ObjectUtil;
import com.example.entity.Account;
import com.example.entity.User;
import com.example.exception.CustomException;
import com.example.mapper.UserMapper;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import jakarta.annotation.Resource;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 普通用户业务处理
 **/
@Service
public class UserService {

    @Resource
    private UserMapper userMapper;

    @Value("${app.default-user-avatar:/files/download/默认头像.jpg}")
    private String defaultUserAvatar;

    /**
     * 新增
     */
    public void add(User user) {
        User dbUser = userMapper.selectByUsername(user.getUsername());
        if (ObjectUtil.isNotNull(dbUser)) {
            throw new CustomException("用户已存在！");
        }
        
        // 验证电话号码是否已绑定
        if (ObjectUtil.isNotEmpty(user.getPhone())) {
            User phoneUser = userMapper.selectByPhone(user.getPhone());
            if (ObjectUtil.isNotNull(phoneUser)) {
                throw new CustomException("该电话号码已被绑定！");
            }
            
            // 验证电话号码格式
            if (!user.getPhone().matches("^1[3-9]\\d{9}$")) {
                throw new CustomException("电话号码格式不正确！");
            }
        } else {
            throw new CustomException("电话号码不能为空！");
        }
        
        if (ObjectUtil.isEmpty(user.getPassword())) {
            user.setPassword("1");
        }
        /*默认名字为用户名*/
        if (ObjectUtil.isEmpty(user.getName())) {
            user.setName(user.getUsername());
        }
        if (ObjectUtil.isEmpty(user.getAvatar())) {
            user.setAvatar(defaultUserAvatar);
        }
        user.setRole("普通用户");
        userMapper.insert(user);
    }

    /**
     * 删除
     */
    public void deleteById(Integer id) {
        userMapper.deleteById(id);
    }

    /**
     * 修改
     */
    public void updateById(User user) {
        // 如果修改了电话号码，需要验证是否被占用
        if (ObjectUtil.isNotEmpty(user.getPhone())) {
            User dbUser = userMapper.selectById(user.getId());
            // 如果电话号码发生了变化
            if (!user.getPhone().equals(dbUser.getPhone())) {
                User phoneUser = userMapper.selectByPhone(user.getPhone());
                if (ObjectUtil.isNotNull(phoneUser) && !phoneUser.getId().equals(user.getId())) {
                    throw new CustomException("该电话号码已被绑定！");
                }
                
                // 验证电话号码格式
                if (!user.getPhone().matches("^1[3-9]\\d{9}$")) {
                    throw new CustomException("电话号码格式不正确！");
                }
            }
        } else {
            throw new CustomException("电话号码不能为空！");
        }
        
        userMapper.updateById(user);
    }

    /**
     * 根据ID查询
     */
    public User selectById(Integer id) {
        return userMapper.selectById(id);
    }

    /**
     * 查询所有
     */
    public List<User> selectAll(User user) {
        return userMapper.selectAll(user);
    }

    /**
     * 分页查询
     */
    public PageInfo<User> selectPage(User user, Integer pageNum, Integer pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<User> list = userMapper.selectAll(user);
        return PageInfo.of(list);
    }

    /**
     * 登录
     */
    public Account login(Account account) {
        Account dbUser = userMapper.selectByUsername(account.getUsername());
        if (ObjectUtil.isNull(dbUser)) {
            throw new CustomException("用户不存在！");
        }
        if (!account.getPassword().equals(dbUser.getPassword())) {
            throw new CustomException("账号或密码错误！");
        }
        dbUser.setRole("普通用户");
        return dbUser;
    }

    /**
     * 修改密码
     */
    public void updatePassword(Account account) {
        User dbUser = userMapper.selectByUsername(account.getUsername());
        if (ObjectUtil.isNull(dbUser)) {
            throw new CustomException("用户不存在！");
        }
        if (!account.getPassword().equals(dbUser.getPassword())) {
            throw new CustomException("原密码错误！");
        }
        dbUser.setPassword(account.getNewPassword());
        userMapper.updateById(dbUser);
    }

    /**
     * 根据电话查询用户
     */
    public User selectByPhone(String phone) {
        return userMapper.selectByPhone(phone);
    }

}

