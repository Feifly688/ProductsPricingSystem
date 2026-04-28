package com.example.controller;

import com.example.common.Result;
import com.example.entity.Feedback;
import com.example.service.FeedbackService;
import jakarta.annotation.Resource;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/feedback")
public class FeedbackController {

    @Resource
    private FeedbackService feedbackService;

    @GetMapping("/user")
    public Result getUserFeedbacks(@RequestParam Integer userId) {
        if (userId == null) {
            return Result.error("请先登录");
        }
        return Result.success(feedbackService.getUserFeedbacks(userId));
    }

    @GetMapping("/list")
    public Result getAllFeedbacks(@RequestParam String role) {
        if (!"管理员".equals(role)) {
            return Result.error("无权访问！");
        }
        return Result.success(feedbackService.getAllFeedbacks());
    }

    @PostMapping
    public Result addFeedback(@RequestBody Feedback feedback) {
        if (feedback.getUserId() == null) {
            return Result.error("请先登录");
        }
        return feedbackService.addFeedback(feedback) ?
                Result.success() :
                Result.error("提交失败");
    }

    @PutMapping("/reply")
    public Result replyFeedback(@RequestBody Feedback feedback, @RequestParam String role) {
        if (!"管理员".equals(role)) {
            return Result.error("无权访问！");
        }
        return feedbackService.replyFeedback(feedback) ?
                Result.success() :
                Result.error("回复失败");
    }

    @DeleteMapping("/{id}")
    public Result deleteFeedback(@PathVariable Integer id, @RequestParam String role) {
        if (!"管理员".equals(role)) {
            return Result.error("无权访问！");
        }
        return feedbackService.deleteFeedback(id) ?
                Result.success() :
                Result.error("删除失败");
    }
}
