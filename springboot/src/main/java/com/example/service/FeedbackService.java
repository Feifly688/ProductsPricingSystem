package com.example.service;

import com.example.entity.Feedback;

import java.util.List;

public interface FeedbackService {
    
    List<Feedback> getUserFeedbacks(Integer userId);
    
    List<Feedback> getAllFeedbacks();
    
    boolean addFeedback(Feedback feedback);
    
    boolean replyFeedback(Feedback feedback);
    
    boolean deleteFeedback(Integer id);
} 