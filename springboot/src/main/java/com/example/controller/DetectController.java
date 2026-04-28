package com.example.controller;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.example.common.Result;
import com.example.service.DetectService;
import jakarta.annotation.Resource;
import jakarta.servlet.http.HttpServletRequest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Base64;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;

@RestController
public class DetectController {
    private static final Logger logger = LoggerFactory.getLogger(DetectController.class);

    @Value("${python.script.path:}")
    private String pythonScriptPath;

    @Value("${python.executable:python}")
    private String pythonExecutable;

    @Value("${conda.env.name:}")
    private String condaEnv;

    @Value("${detection.process.timeout:60}")
    private long processTimeoutSeconds;

    @Value("${temp.image.dir:}")
    private String tempImageDir;

    @Value("${temp.image.prefix:uploaded_image}")
    private String tempImagePrefix;

    @Resource
    private DetectService detectService;

    @GetMapping("/getPriceDatabase")
    public Result getPriceDatabase() {
        Map<String, Object> map = detectService.getPriceData();
        return Result.success(map);
    }

    @PostMapping(value = "/runDetect", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<String> runDetection(@RequestParam("image") MultipartFile image, HttpServletRequest request) {
        long startTime = System.currentTimeMillis();
        Path tempFile = null;

        try {
            if (image == null || image.isEmpty()) {
                return detectionError(400, "上传图片为空", null, null, null);
            }

            Path scriptPath = Paths.get(pythonScriptPath).toAbsolutePath().normalize();
            if (!Files.isRegularFile(scriptPath)) {
                return detectionError(500, "Python 检测脚本不存在: " + scriptPath, null, null, null);
            }

            Path uploadDir = resolveTempUploadDir();
            Files.createDirectories(uploadDir);
            tempFile = Files.createTempFile(uploadDir, tempImagePrefix, ".jpg");
            try (InputStream inputStream = image.getInputStream()) {
                Files.copy(inputStream, tempFile, StandardCopyOption.REPLACE_EXISTING);
            }

            List<String> command = buildCommand(scriptPath, tempFile);
            Map<String, Object> processData = new HashMap<>();
            processData.put("originalFilename", image.getOriginalFilename());
            processData.put("contentType", image.getContentType());
            processData.put("tempFilePath", tempFile.toAbsolutePath().toString());
            processData.put("pythonScriptPath", scriptPath.toString());
            processData.put("pythonExecutable", pythonExecutable);
            processData.put("condaEnv", condaEnv);
            logger.info("开始执行商品检测: {}", JSONObject.toJSONString(processData));

            ProcessBuilder processBuilder = new ProcessBuilder(command).redirectErrorStream(false);
            Path scriptParent = scriptPath.getParent();
            if (scriptParent != null) {
                processBuilder.directory(scriptParent.toFile());
            }

            Process process = processBuilder.start();
            StringBuilder output = new StringBuilder();
            StringBuilder errorOutput = new StringBuilder();
            CompletableFuture<Void> stdoutFuture = readProcessStream(process.getInputStream(), output);
            CompletableFuture<Void> stderrFuture = readProcessStream(process.getErrorStream(), errorOutput);

            boolean finished = process.waitFor(processTimeoutSeconds, TimeUnit.SECONDS);
            if (!finished) {
                process.destroyForcibly();
                CompletableFuture.allOf(stdoutFuture, stderrFuture).get(2, TimeUnit.SECONDS);
                return detectionError(504, "Detection timeout", command, output.toString(), errorOutput.toString());
            }
            CompletableFuture.allOf(stdoutFuture, stderrFuture).get(5, TimeUnit.SECONDS);

            int exitCode = process.exitValue();
            long executeTime = System.currentTimeMillis() - startTime;
            String stdoutStr = output.toString().trim();
            String stderrStr = errorOutput.toString().trim();

            if (exitCode != 0) {
                logger.error("检测失败, exitCode={}, stderr={}", exitCode, stderrStr);
                return detectionError(500, "Detection failed, exitCode=" + exitCode, command, stdoutStr, stderrStr);
            }

            String jsonOutput = extractDetectionJson(stdoutStr);
            logger.info("检测结果: {}", jsonOutput);
            JSONObject jsonObject = JSONObject.parseObject(jsonOutput);
            JSONArray detections = jsonObject.getJSONArray("detections");
            if (detections == null) {
                detections = new JSONArray();
            }
            float detectionTime = jsonObject.getFloatValue("detection_time");
            String processedImage = jsonObject.getString("processed_image");

            Map<String, Object> priceData = detectService.getPriceData();
            BigDecimal totalPrice = BigDecimal.ZERO;
            for (int i = 0; i < detections.size(); i++) {
                JSONObject detection = detections.getJSONObject(i);
                String productName = detection.getString("name");
                int count = detection.getIntValue("count");
                BigDecimal price = getPrice(priceData.get(productName));
                totalPrice = totalPrice.add(price.multiply(BigDecimal.valueOf(count)));

                try {
                    detectService.updateProductSales(productName, count);
                    logger.info("商品 {} 销售量更新成功", productName);
                } catch (Exception e) {
                    logger.error("更新商品 {} 销售量失败: {}", productName, e.getMessage());
                }
            }

            String imagePath = saveProcessedImage(processedImage);
            JSONObject responseJson = new JSONObject();
            responseJson.put("code", "200");
            responseJson.put("data", detections);
            responseJson.put("file_name", imagePath.isEmpty() ? "" : imagePath.substring(imagePath.lastIndexOf('/') + 1));
            responseJson.put("file_path", imagePath);
            responseJson.put("inference_time", detectionTime);
            responseJson.put("run_duration", executeTime / 1000.0f);
            responseJson.put("processed_image", processedImage);
            responseJson.put("total_price", totalPrice);

            return ResponseEntity.ok(responseJson.toJSONString());
        } catch (Exception e) {
            logger.error("处理图片检测时发生错误", e);
            return detectionError(500, "Internal server error: " + e.getMessage(), null, null, stackTraceToString(e));
        } finally {
            if (tempFile != null) {
                try {
                    Files.deleteIfExists(tempFile);
                } catch (IOException e) {
                    logger.warn("删除临时图片失败: {}", tempFile, e);
                }
            }
        }
    }

    private List<String> buildCommand(Path scriptPath, Path tempFile) {
        List<String> command = new ArrayList<>();
        if (condaEnv != null && !condaEnv.isBlank()) {
            command.addAll(Arrays.asList("conda", "run", "-n", condaEnv, "python"));
        } else {
            validatePythonExecutable();
            command.add(pythonExecutable);
        }
        command.add(scriptPath.toString());
        command.add(tempFile.toAbsolutePath().toString());
        return command;
    }

    private void validatePythonExecutable() {
        if (pythonExecutable == null || pythonExecutable.isBlank()) {
            throw new IllegalStateException("python.executable 未配置");
        }
        if (pythonExecutable.contains("/") || pythonExecutable.contains("\\")) {
            Path executablePath = Paths.get(pythonExecutable).toAbsolutePath().normalize();
            if (!Files.isRegularFile(executablePath) || !Files.isExecutable(executablePath)) {
                throw new IllegalStateException("Python 可执行文件不存在或不可执行: " + executablePath);
            }
        }
    }

    private Path resolveTempUploadDir() {
        if (tempImageDir != null && !tempImageDir.isBlank()) {
            return Paths.get(tempImageDir).toAbsolutePath().normalize();
        }
        return Paths.get(System.getProperty("java.io.tmpdir")).toAbsolutePath().normalize();
    }

    private CompletableFuture<Void> readProcessStream(InputStream stream, StringBuilder target) {
        return CompletableFuture.runAsync(() -> {
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(stream, StandardCharsets.UTF_8))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    target.append(line).append(System.lineSeparator());
                }
            } catch (IOException e) {
                target.append("读取进程输出失败: ").append(e.getMessage());
            }
        });
    }

    private BigDecimal getPrice(Object priceObj) {
        if (priceObj == null) {
            return BigDecimal.ZERO;
        }
        if (priceObj instanceof Map<?, ?> priceMap) {
            return getPrice(priceMap.get("price"));
        }
        if (priceObj instanceof BigDecimal) {
            return (BigDecimal) priceObj;
        }
        if (priceObj instanceof Number) {
            return BigDecimal.valueOf(((Number) priceObj).doubleValue());
        }
        return new BigDecimal(String.valueOf(priceObj));
    }

    private String extractDetectionJson(String stdout) {
        if (stdout == null || stdout.isBlank()) {
            throw new IllegalStateException("Python 检测脚本没有输出结果");
        }

        String trimmed = stdout.trim();
        int jsonStart = trimmed.indexOf("{\"detections\"");
        if (jsonStart < 0) {
            jsonStart = trimmed.indexOf("{'detections'");
        }
        if (jsonStart < 0 && trimmed.startsWith("{")) {
            jsonStart = 0;
        }
        if (jsonStart < 0) {
            throw new IllegalStateException("Python 检测脚本输出不是合法 JSON: " + truncate(trimmed, 500));
        }

        int jsonEnd = trimmed.lastIndexOf('}');
        if (jsonEnd < jsonStart) {
            throw new IllegalStateException("Python 检测脚本 JSON 输出不完整: " + truncate(trimmed, 500));
        }
        return trimmed.substring(jsonStart, jsonEnd + 1);
    }

    private ResponseEntity<String> detectionError(int status, String message, List<String> command, String stdout, String stderr) {
        JSONObject errorJson = new JSONObject();
        errorJson.put("code", String.valueOf(status));
        errorJson.put("msg", message);
        if (command != null) {
            errorJson.put("command", String.join(" ", command));
        }
        if (stdout != null && !stdout.isBlank()) {
            errorJson.put("stdout", truncate(stdout, 2000));
        }
        if (stderr != null && !stderr.isBlank()) {
            errorJson.put("stderr", truncate(stderr, 4000));
        }
        logger.error("商品检测接口失败: {}", errorJson.toJSONString());
        return ResponseEntity.status(status).contentType(MediaType.APPLICATION_JSON).body(errorJson.toJSONString());
    }

    private String truncate(String value, int maxLength) {
        if (value == null || value.length() <= maxLength) {
            return value;
        }
        return value.substring(0, maxLength) + "...";
    }

    private String stackTraceToString(Exception e) {
        StringWriter sw = new StringWriter();
        e.printStackTrace(new PrintWriter(sw));
        return sw.toString();
    }

    private String saveProcessedImage(String base64Image) {
        if (base64Image == null || base64Image.isBlank()) {
            return "";
        }
        try {
            byte[] imageBytes = Base64.getDecoder().decode(base64Image);
            String fileName = "detected_" + System.currentTimeMillis() + ".jpg";
            Path resultsImagesDir = Paths.get(pythonScriptPath).toAbsolutePath().normalize()
                    .getParent()
                    .resolve("results")
                    .resolve("images");
            File dir = resultsImagesDir.toFile();
            if (!dir.exists() && !dir.mkdirs()) {
                throw new IOException("无法创建结果图片目录: " + resultsImagesDir);
            }
            File outFile = resultsImagesDir.resolve(fileName).toFile();
            try (FileOutputStream fos = new FileOutputStream(outFile)) {
                fos.write(imageBytes);
            }
            return "/results/images/" + fileName;
        } catch (Exception e) {
            logger.error("保存处理后的图片失败", e);
            return "";
        }
    }
}
