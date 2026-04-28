package com.example.mapper;

import com.example.entity.PricingRecord;
import com.example.entity.PricingRecordItem;
import org.apache.ibatis.annotations.*;

import java.util.List;

@Mapper
public interface PricingRecordMapper {

    @Insert("INSERT INTO pricing_record (id, image_path, total_price, item_count, detection_duration, execute_duration, create_time, create_user_id, create_user_name) " +
            "VALUES (#{id}, #{imagePath}, #{totalPrice}, #{itemCount}, #{detectionDuration}, #{executeDuration}, #{createTime}, #{createUserId}, #{createUserName})")
    void insertRecord(PricingRecord record);

    @Insert("INSERT INTO pricing_record_item (id, record_id, name, count, price) " +
            "VALUES (#{id}, #{recordId}, #{name}, #{count}, #{price})")
    void insertRecordItem(PricingRecordItem item);

    @Select("SELECT * FROM pricing_record ORDER BY create_time DESC")
    @Results({
            @Result(property = "id", column = "id"),
            @Result(property = "items", column = "id", javaType = List.class,
                    many = @Many(select = "selectItemsByRecordId"))
    })
    List<PricingRecord> selectAllRecords();

    /**
     * 根据记录ID查询明细
     */
    @Select("SELECT * FROM pricing_record_item WHERE record_id = #{recordId}")
    List<PricingRecordItem> selectItemsByRecordId(String recordId);

    /**
     * 批量插入商品明细（提升性能）
     */
    @Insert("<script>" +
            "INSERT INTO pricing_record_item (id, record_id, name, count, price) " +
            "VALUES " +
            "<foreach collection='list' item='item' separator=','>" +
            "(#{item.id}, #{item.recordId}, #{item.name}, #{item.count}, #{item.price})" +
            "</foreach>" +
            "</script>")
    void batchInsertRecordItems(@Param("list") List<PricingRecordItem> items);

    /**
     * 根据ID查询单条计价主记录（关联明细）
     */
    @Select("SELECT * FROM pricing_record WHERE id = #{id}")
    @Results({
            @Result(property = "id", column = "id"),
            @Result(property = "items", column = "id", javaType = List.class,
                    many = @Many(select = "selectItemsByRecordId"))
    })
    PricingRecord selectRecordById(String id);

    /**
     * 根据记录ID删除关联的商品明细
     */
    @Delete("DELETE FROM pricing_record_item WHERE record_id = #{recordId}")
    void deleteRecordItemsByRecordId(String recordId);

    /**
     * 根据ID删除计价主记录
     */
    @Delete("DELETE FROM pricing_record WHERE id = #{id}")
    int deleteRecordById(String id);

    /**
     * 批量删除主记录（优化批量删除性能）
     */
    @Delete("<script>" +
            "DELETE FROM pricing_record WHERE id IN " +
            "<foreach collection='list' item='id' open='(' separator=',' close=')'>" +
            "#{id}" +
            "</foreach>" +
            "</script>")
    int batchDeleteRecords(@Param("list") List<String> ids);

    /**
     * 批量删除明细记录（优化批量删除性能）
     */
    @Delete("<script>" +
            "DELETE FROM pricing_record_item WHERE record_id IN " +
            "<foreach collection='list' item='id' open='(' separator=',' close=')'>" +
            "#{id}" +
            "</foreach>" +
            "</script>")
    void batchDeleteRecordItems(@Param("list") List<String> ids);
}
