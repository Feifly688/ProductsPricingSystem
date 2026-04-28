package com.example.controller;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.example.common.Result;
import com.example.entity.Account;
import com.example.entity.PricingRecord;
import com.example.entity.PricingRecordItem;
import com.example.service.DetectService;
import com.example.service.PricingRecordService;
import jakarta.annotation.Resource;
import jakarta.servlet.http.HttpServletRequest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.*;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.util.*;

@RestController
public class DetectController {
    private static final Logger logger = LoggerFactory.getLogger(DetectController.class);

    @Value("${python.script.path:}")
    private String pythonScriptPath;

    @Resource
    private DetectService detectService;

    @Resource
    private PricingRecordService pricingRecordService;

    /**
     * 获取价格列表
     */
    @GetMapping("/getPriceDatabase")
    public Result getPriceDatabase() {
        Map<String, Object> map = detectService.getPriceData();
        return Result.success(map);
    }

    /**
     * 执行计价操作
     */
    @PostMapping(value = "/runDetect", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<String> runDetection(@RequestParam("image") MultipartFile image, HttpServletRequest request) {
        long startTime = System.currentTimeMillis();

        try {
            // 保存上传的图片
            File tempFile = File.createTempFile("uploaded_image", ".jpg");
            image.transferTo(tempFile);

            // 构建命令
            String pythonScriptPath = "D:/software/IntelliJIDEA2025.3.2/Projects/ProductsPricingSystem/deepLearning/yolov8/predict_upload.py";
            String condaEnv = "yolov8";
            String command = String.format("cmd /c conda activate %s && python %s %s", condaEnv, pythonScriptPath, tempFile.getAbsolutePath());

            Map<String, Object> beforeProcessData = new HashMap<>();
            beforeProcessData.put("originalFilename", image.getOriginalFilename());
            beforeProcessData.put("contentType", image.getContentType());
            beforeProcessData.put("tempFilePath", tempFile.getAbsolutePath());
            beforeProcessData.put("pythonScriptPath", pythonScriptPath);
            beforeProcessData.put("condaEnv", condaEnv);

            // 执行Python脚本
            Process process = Runtime.getRuntime().exec(command);
            InputStream is = process.getInputStream();
            InputStreamReader isr = new InputStreamReader(is);
            BufferedReader br = new BufferedReader(isr);
            StringBuilder output = new StringBuilder();
            String line;
            while ((line = br.readLine()) != null) {
                output.append(line);
            }
            int exitCode = process.waitFor();

            long executeTime = System.currentTimeMillis() - startTime;

            StringBuilder errorOutput = new StringBuilder();
            try (BufferedReader errBr = new BufferedReader(new InputStreamReader(process.getErrorStream()))) {
                String errLine;
                while ((errLine = errBr.readLine()) != null) {
                    errorOutput.append(errLine);
                }
            }

            Map<String, Object> afterProcessData = new HashMap<>();
            afterProcessData.put("exitCode", exitCode);
            String stdoutStr = output.toString();
            afterProcessData.put("stdoutSnippet", stdoutStr.length() > 500 ? stdoutStr.substring(0, 500) : stdoutStr);
            String stderrStr = errorOutput.toString();
            afterProcessData.put("stderrSnippet", stderrStr.length() > 500 ? stderrStr.substring(0, 500) : stderrStr);
            afterProcessData.put("executeTimeMs", executeTime);

            if (exitCode == 0) {
                String result = output.toString();
                logger.info("检测结果: {}", result);

                JSONObject jsonObject = JSONObject.parseObject(result);
                JSONArray detections = jsonObject.getJSONArray("detections");
                float detectionTime = jsonObject.getFloatValue("detection_time");
                String processedImage = jsonObject.getString("processed_image");

                logger.info("检测到的商品数量: {}", detections.size());

                // 获取价格数据
                Map<String, Object> priceData = detectService.getPriceData();
                BigDecimal totalPrice = BigDecimal.ZERO;
                List<PricingRecordItem> itemList = new ArrayList<>();

                // 处理每个检测到的商品
                for (int i = 0; i < detections.size(); i++) {
                    JSONObject detection = detections.getJSONObject(i);
                    String productName = detection.getString("name");
                    int count = detection.getIntValue("count");

                    // 获取单价
                    Object priceObj = priceData.get(productName);
                    BigDecimal price = BigDecimal.ZERO;
                    if (priceObj != null) {
                        if (priceObj instanceof Double) {
                            price = BigDecimal.valueOf((Double) priceObj);
                        } else if (priceObj instanceof String) {
                            price = new BigDecimal((String) priceObj);
                        }
                    }

                    BigDecimal subtotal = price.multiply(new BigDecimal(count));
                    totalPrice = totalPrice.add(subtotal);

                    // 添加到明细列表
                    PricingRecordItem item = new PricingRecordItem();
                    item.setId(UUID.randomUUID().toString().replace("-", ""));
                    item.setName(productName);
                    item.setCount(count);
                    item.setPrice(price);
                    itemList.add(item);

                    // 更新商品销售量
                    try {
                        detectService.updateProductSales(productName, count);
                        logger.info("商品 {} 销售量更新成功", productName);
                    } catch (Exception e) {
                        logger.error("更新商品 {} 销售量失败: {}", productName, e.getMessage());
                    }
                }

                // 保存检测记录到数据库（仅在此处保存图片一次，避免重复写入）
                String imagePath = saveProcessedImage(processedImage);
                // 构建返回结果（与前端 Predict.vue 期望的 code/data/file_name/file_path/inference_time/run_duration 一致）
                JSONObject responseJson = new JSONObject();
                responseJson.put("code", "200");
                responseJson.put("data", detections);
                responseJson.put("file_name", imagePath.isEmpty() ? "" : imagePath.substring(imagePath.lastIndexOf('/') + 1));
                responseJson.put("file_path", imagePath);
                responseJson.put("inference_time", detectionTime);
                responseJson.put("run_duration", executeTime / 1000.0f);
                responseJson.put("processed_image", processedImage);

                return ResponseEntity.ok(responseJson.toJSONString());
            } else {
                logger.error("检测失败，退出代码: {}", exitCode);
                return ResponseEntity.status(500).body("Detection failed");
            }
        } catch (IOException | InterruptedException e) {
            logger.error("处理图片检测时发生错误", e);
            return ResponseEntity.status(500).body("Internal server error");
        }
    }

    /**
     * 保存处理后的图片到 yolov8 的 results/images
     * 绝对路径：.../deepLearning/yolov8/results/images
     */
    private String saveProcessedImage(String base64Image) {
        try {
            byte[] imageBytes = Base64.getDecoder().decode(base64Image);
            String fileName = "detected_" + System.currentTimeMillis() + ".jpg";
            Path resultsImagesDir = Paths.get(pythonScriptPath).getParent().resolve("results").resolve("images");
            File dir = resultsImagesDir.toFile();
            if (!dir.exists()) {
                dir.mkdirs();
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
