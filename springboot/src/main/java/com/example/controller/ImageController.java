package com.example.controller;

import jakarta.servlet.ServletOutputStream;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * 提供检测结果图片访问：
 * - /images/detected_xxx.jpg → 与 DetectController.saveProcessedImage 保存路径一致；
 * - /results/images/xxx.jpg → 兼容旧记录（Python 脚本输出目录）。
 */
@RestController
public class ImageController {

    /** 与 DetectController.saveProcessedImage 中 uploadPath 保持一致 */
    private static final String IMAGE_DIR = "D:/upload/images/";

    @Value("${python.script.path:}")
    private String pythonScriptPath;

    @GetMapping(value = "/images/{fileName:.+}", produces = MediaType.IMAGE_JPEG_VALUE)
    public void serveImage(@PathVariable String fileName, HttpServletResponse response) throws IOException {
        Path base = Paths.get(IMAGE_DIR).toAbsolutePath().normalize();
        Path file = base.resolve(fileName).normalize();
        if (!file.startsWith(base) || !Files.isRegularFile(file)) {
            response.sendError(HttpServletResponse.SC_NOT_FOUND);
            return;
        }
        response.setContentType(MediaType.IMAGE_JPEG_VALUE);
        try (ServletOutputStream out = response.getOutputStream()) {
            Files.copy(file, out);
        }
    }

    /** 兼容旧记录：/results/images/uploaded_xxx.jpg 对应 yolov8 脚本输出目录 */
    @GetMapping(value = "/results/images/{fileName:.+}", produces = MediaType.IMAGE_JPEG_VALUE)
    public void serveResultsImage(@PathVariable String fileName, HttpServletResponse response) throws IOException {
        if (pythonScriptPath == null || pythonScriptPath.isEmpty()) {
            response.sendError(HttpServletResponse.SC_NOT_FOUND);
            return;
        }
        Path base = Paths.get(pythonScriptPath).getParent().resolve("results").resolve("images").toAbsolutePath().normalize();
        Path file = base.resolve(fileName).normalize();
        if (!file.startsWith(base) || !Files.isRegularFile(file)) {
            response.sendError(HttpServletResponse.SC_NOT_FOUND);
            return;
        }
        response.setContentType(MediaType.IMAGE_JPEG_VALUE);
        try (ServletOutputStream out = response.getOutputStream()) {
            Files.copy(file, out);
        }
    }
}
