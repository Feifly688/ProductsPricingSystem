/**
 * FileController
 *
 * @author Feiqi
 * @date 2025/1/6  18:55
 */
package com.example.controller;

import cn.hutool.core.io.FileUtil;
import com.example.common.Result;
import jakarta.servlet.ServletOutputStream;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.UUID;

/**
 * 文件前端操作接口
 */
@RestController
@RequestMapping("/files")
public class FileController {

    @Value("${file.storage-dir:files}")
    private String storageDir;

    @Value("${fileBaseUrl}")
    private String fileBaseUrl;
    @Value("${model.base-path}")
    private String basePath;

    private static final List<String> ALLOWED_EXTENSIONS = List.of(
            "jpg", "jpeg", "png", "gif", "bmp", "webp",
            "pdf", "doc", "docx", "txt", "csv", "json", "xml"
    );

    private String sanitizeFilename(String originalFilename) {
        if (originalFilename == null || originalFilename.isBlank()) {
            return UUID.randomUUID() + ".bin";
        }
        // 提取扩展名
        String ext = "";
        int dotIndex = originalFilename.lastIndexOf('.');
        if (dotIndex > 0) {
            ext = originalFilename.substring(dotIndex + 1).toLowerCase();
        }
        // 校验扩展名白名单，不在白名单内一律改成 .bin
        if (!ALLOWED_EXTENSIONS.contains(ext)) {
            ext = "bin";
        }
        // UUID 重命名 — 彻底阻断路径穿越和文件名注入
        return UUID.randomUUID() + "." + ext;
    }

    /**
     * 文件上传（安全加固版）
     */
    @PostMapping("/upload")
    public Result upload(MultipartFile file) {
        if (file == null || file.isEmpty()) {
            return Result.error("上传文件为空");
        }
        String safeFileName = sanitizeFilename(file.getOriginalFilename());
        Path storagePath = Paths.get(storageDir).toAbsolutePath().normalize();
        Path realFilePath = storagePath.resolve(safeFileName).normalize();
        // 二次校验：确保解析后的路径仍在 storageDir 内
        if (!realFilePath.startsWith(storagePath)) {
            return Result.error("非法文件名");
        }
        try {
            if (!FileUtil.isDirectory(storagePath.toString())) {
                FileUtil.mkdir(storagePath.toString());
            }
            FileUtil.writeBytes(file.getBytes(), realFilePath.toString());
        } catch (IOException e) {
            System.out.println("文件上传错误！");
        }
        String url = fileBaseUrl + "/files/download/" + safeFileName;
        return Result.success(url);
    }

    /**
     * 文件下载（已内置路径穿越保护）
     */
    @GetMapping("/download/{fileName}")
    public void download(@PathVariable String fileName, HttpServletResponse response) {
        // 设置下载文件http响应头
        response.setHeader("Content-Disposition", "attachment;filename=" + URLEncoder.encode(fileName, StandardCharsets.UTF_8));
        Path storagePath = Paths.get(storageDir).toAbsolutePath().normalize();
        Path realFilePath = storagePath.resolve(fileName).normalize();
        if (!realFilePath.startsWith(storagePath)) {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            return;
        }
        try {
            // 通过文件的存储路径拿到文件字节数组
            byte[] bytes = FileUtil.readBytes(realFilePath.toString());
            ServletOutputStream os = response.getOutputStream();
            // 将文件字节数组写出到文件流
            os.write(bytes);
            os.flush();
            os.close();
        } catch (IOException e) {
            System.out.println("文件下载错误！");
        }
    }

    @GetMapping("/training-log/{modelName}")
    public Result getTrainingLog(
            @PathVariable String modelName
    ) {
        try {
            String logPath = Paths.get(basePath, modelName, "train", "training_log.json").toString();
            String content = Files.readString(Path.of(logPath));
            return Result.success(content);
        } catch (IOException e) {
            return Result.error("File Not Found");
        }
    }
}
