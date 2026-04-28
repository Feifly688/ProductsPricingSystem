package com.example.mapper;

import com.example.entity.Feedback;
import java.util.List;
import org.apache.ibatis.annotations.Delete;

public interface FeedbackMapper {
    
    List<Feedback> selectByUserId(Integer userId);
    
    List<Feedback> selectAll();
    
    int insert(Feedback feedback);
    
    int updateReply(Feedback feedback);
    
    @Delete("DELETE FROM feedback WHERE id = #{id}")
    int deleteById(Integer id);
} 