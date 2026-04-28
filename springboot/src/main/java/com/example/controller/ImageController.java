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

@RestController
public class ImageController {

    @Value("${app.image-dir:}")
    private String imageDir;

    @Value("${python.script.path:}")
    private String pythonScriptPath;

    @GetMapping(value = "/images/{fileName:.+}", produces = MediaType.IMAGE_JPEG_VALUE)
    public void serveImage(@PathVariable String fileName, HttpServletResponse response) throws IOException {
        Path base = resolveImageBase();
        serveFile(base, fileName, response);
    }

    @GetMapping(value = "/results/images/{fileName:.+}", produces = MediaType.IMAGE_JPEG_VALUE)
    public void serveResultsImage(@PathVariable String fileName, HttpServletResponse response) throws IOException {
        if (pythonScriptPath == null || pythonScriptPath.isEmpty()) {
            response.sendError(HttpServletResponse.SC_NOT_FOUND);
            return;
        }
        Path base = Paths.get(pythonScriptPath).getParent().resolve("results").resolve("images").toAbsolutePath().normalize();
        serveFile(base, fileName, response);
    }

    private Path resolveImageBase() {
        if (imageDir != null && !imageDir.isBlank()) {
            return Paths.get(imageDir).toAbsolutePath().normalize();
        }
        return Paths.get(System.getProperty("user.dir"), "images").toAbsolutePath().normalize();
    }

    private void serveFile(Path base, String fileName, HttpServletResponse response) throws IOException {
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
