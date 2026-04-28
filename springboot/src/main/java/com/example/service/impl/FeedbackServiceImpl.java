package com.example.service.impl;

import com.example.entity.Feedback;
import com.example.mapper.FeedbackMapper;
import com.example.service.FeedbackService;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;

import java.util.Date;
import java.util.List;

@Service
public class FeedbackServiceImpl implements FeedbackService {

    @Resource
    private FeedbackMapper feedbackMapper;

    @Override
    public List<Feedback> getUserFeedbacks(Integer userId) {
        return feedbackMapper.selectByUserId(userId);
    }

    @Override
    public List<Feedback> getAllFeedbacks() {
        return feedbackMapper.selectAll();
    }

    @Override
    public boolean addFeedback(Feedback feedback) {
        feedback.setCreateTime(new Date());
        feedback.setStatus(0); //0为未读
        return feedbackMapper.insert(feedback) > 0;
    }

    @Override
    public boolean replyFeedback(Feedback feedback) {
        feedback.setStatus(1);  // 1-已读
        feedback.setReplyTime(new Date());
        return feedbackMapper.updateReply(feedback) > 0;
    }

    @Override
    public boolean deleteFeedback(Integer id) {
        return feedbackMapper.deleteById(id) > 0;
    }
}
