package com.example.mapper;

import org.apache.ibatis.annotations.MapKey;

import java.util.Map;

public interface DetectMapper {
    @MapKey("name")
    Map<String, Object> getPriceData();
}
