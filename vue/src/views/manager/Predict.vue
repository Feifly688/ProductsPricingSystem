<!--
*@
*@author Feiqi
*@date 2025/3/27 10:13
-->
<template>
    <div class="container">
        <div v-if="Object.keys(priceDatabase).length === 0" class="loading-tip">
            正在加载商品价格数据...
        </div>
        <div v-else>
            <!-- 标题 -->
            <h1>商品检测计价</h1>
            <!-- 上传区域 -->
            <div class="upload-box">
                <input
                        ref="fileInput"
                        accept="image/*"
                        hidden
                        type="file"
                        @change="handleFileUpload"
                >
                <button v-if="!uploading" class="upload-btn" @click="triggerUpload">
                    <span>上传商品图片</span>
                </button>
                <button v-if="uploading" class="upload-btn">
                    <span>检测进行中...</span>
                </button>
                <button class="upload-btn" @click="openCamera" v-if="!isCameraOpen">
                    打开摄像头
                </button>
                <button v-if="isCameraOpen" class="upload-btn" @click="takePhoto">
                    拍照
                </button>
                <video v-if="isCameraOpen" ref="video" autoplay height="400" width="500"></video>
                <canvas v-if="isCameraOpen" ref="canvas" style="display: none;"></canvas>
                <div v-if="previewImage || detectedImagePath" class="preview">
                    <!-- 根据是否有检测结果图片来显示不同的图片 -->
                    <el-image
                            v-if="!isCameraOpen"
                            :preview-src-list="[detectedImagePath || previewImage]"
                            :src="detectedImagePath || previewImage"
                            preview-teleported
                            style="width: 500px; height: 400px; border-radius: 4px; box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);"
                    ></el-image>
                </div>
            </div>
            <!-- 检测结果 -->
            <div v-if="results&&!isCameraOpen" class="results">
                <div class="detection-time">检测用时：{{ detectionDuration.toFixed(2) }} ms</div> <!-- 显示检测用时 -->
                <div class="detection-time">运行时长：{{ executeDuration.toFixed(2) }} s</div> <!-- 显示运行时长 -->
                <h2>检测结果</h2>
                <div class="result-list">
                    <div v-for="(item, index) in results.items" :key="index" class="result-item">
                        <span class="name">{{ item.name }} ×{{ item.count }}</span>
                        <span class="price">
                            ¥{{ item.price.toFixed(2) }} × {{ item.count }} = ¥{{ (item.price * item.count).toFixed(2) }}
                            <span v-if="item.price === 0" class="warn-tip">(未定价)</span>
                        </span>
                    </div>
                </div>
                <div class="total-price">
                    总金额：<span>¥{{ results.total.toFixed(2) }}</span>
                </div>
                <!-- 移除保存按钮 -->
            </div>
            <!-- 错误提示 -->
            <div v-if="error" class="error-message">
                {{ error }}
            </div>
        </div>
    </div>
</template>

<script setup>
import request from "../../utils/request";
import {nextTick, onMounted, ref, watch} from 'vue';
import {ElImage, ElMessage} from 'element-plus';
import {useRouter} from 'vue-router';

const router = useRouter();
const fileInput = ref(null);
const uploading = ref(false);
const previewImage = ref(null);
const detectedImagePath = ref(null);
/** 供保存记录使用的短路径（仅路径，非 base64），满足数据库 image_path varchar(255) */
const imagePathForSave = ref(null);
const results = ref(null);
const error = ref(null);
const priceDatabase = ref({});
const detectionDuration = ref(0);
const executeDuration = ref(0);
const isCameraOpen = ref(false);
const video = ref(null);
const canvas = ref(null);
const savingRecord = ref(false); // 添加保存状态变量
let cameraStream = null;

// 触发文件选择
const triggerUpload = () => {
    fileInput.value.click();
};

// 获取价格数据库
const fetchPriceDatabase = async () => {
    const response = await request.get('/getPriceDatabase');
    priceDatabase.value = response.data;
    console.log('价格数据库:', priceDatabase.value);
};

// 处理文件上传和检测逻辑
const processImage = async (file) => {
    if (!file) return;
    try {
        uploading.value = true;
        error.value = null;
        results.value = null;
        detectedImagePath.value = null;
        imagePathForSave.value = null;
        // 显示预览
        previewImage.value = URL.createObjectURL(file);
        // 创建FormData
        const formData = new FormData();
        formData.append('image', file);
        // 发送检测请求
        const response = await request.post('/runDetect', formData);
        let data;
        try {
            // 尝试解析响应数据为JSON
            data = typeof response === 'string' ? JSON.parse(response) : response;
        } catch (parseError) {
            // 解析失败，抛出错误
            throw new Error('Invalid JSON response from server');
        }
        // 检查响应数据是否有效
        if (data && typeof data.code === 'string') {
            if (data.code === '200') {
                const detections = data.data;
                const fileName = data.file_name;
                const filePath = data.file_path; // 获取新的文件路径
                detectionDuration.value = data.inference_time; // 获取检测用时
                executeDuration.value = data.run_duration; // 获取运行时长

                // 设置检测结果图片：优先使用后端返回的 base64，否则用 file_path / file_name
                if (data.processed_image) {
                    detectedImagePath.value = `data:image/jpeg;base64,${data.processed_image}`;
                } else if (filePath) {
                    detectedImagePath.value = filePath;
                } else if (fileName) {
                    detectedImagePath.value = `/results/images/${fileName}`;
                } else {
                    detectedImagePath.value = null;
                }
                // 保存记录时只用短路径，避免 image_path 超长（varchar(255)）
                imagePathForSave.value = filePath || (fileName ? `/results/images/${fileName}` : null);

                results.value = {
                    items: detections.map(item => ({
                        name: item.name,
                        count: item.count,
                        price: priceDatabase.value[item.name]?.price || 0
                    })),
                    total: detections.reduce(
                            (sum, item) => sum + (priceDatabase.value[item.name]?.price || 0) * item.count,
                            0
                    )
                };
                console.log('检测结果图片路径:', detectedImagePath.value);
            } else {
                throw new Error(data.msg);
            }
        } else if (data && data.error) {
            // 处理包含错误信息的响应
            throw new Error(data.message || data.error);
        } else {
            throw new Error('无效的响应数据');
        }
    } catch (err) {
        error.value = `${err.message}`;
    } finally {
        uploading.value = false;
    }
};

// 处理文件上传
const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    await processImage(file);
};

// 打开摄像头
const openCamera = async () => {
    try {
        cameraStream = await navigator.mediaDevices.getUserMedia({video: true});
        isCameraOpen.value = true;
    } catch (err) {
        error.value = `无法打开摄像头: ${err.message}`;
    }
};

// 拍照
const takePhoto = () => {
    isCameraOpen.value = false
    const context = canvas.value.getContext('2d');
    context.drawImage(video.value, 0, 0, canvas.value.width, canvas.value.height);
    canvas.value.toBlob(async (blob) => {
        const file = new File([blob], 'photo.jpg', {type: 'image/jpeg'});
        await processImage(file);
        isCameraOpen.value = false;
        cameraStream.getTracks().forEach(track => track.stop());
    }, 'image/jpeg');
};

// 监控 isCameraOpen 的变化
watch(isCameraOpen, async (newValue) => {
    if (newValue) {
        await nextTick();
        if (video.value) {
            video.value.srcObject = cameraStream;
        }
    }
});

// 保存计价记录功能
const savePricingRecord = async () => {
    if (!results.value) {
        ElMessage.warning('没有可保存的计价结果');
        return;
    }

    try {
        savingRecord.value = true;

        // 构建保存的数据结构（imagePath 必须为短路径，数据库 image_path varchar(255)，不能传 base64）
        const shortPath = imagePathForSave.value || (detectedImagePath.value && !String(detectedImagePath.value).startsWith('data:') ? detectedImagePath.value : '');
        const recordData = {
            imagePath: shortPath || '',
            totalPrice: results.value.total, // 总价格
            itemCount: results.value.items.reduce((sum, item) => sum + item.count, 0), // 商品总数量
            detectionDuration: detectionDuration.value, // 检测用时
            executeDuration: executeDuration.value, // 运行用时
            itemsJson: JSON.stringify(results.value.items) // 将商品列表转为JSON字符串
        };

        console.log('发送保存请求数据:', JSON.stringify(recordData, null, 2));

        // 保存到数据库
        const response = await request.post('/pricingRecord', recordData);
        console.log('保存记录响应:', response);

        if (response.code === '200') {
            ElMessage.success('计价记录已保存');
        } else {
            throw new Error(response.msg || '保存失败');
        }
    } catch (error) {
        console.error('保存计价记录失败:', error);
        if (error.response) {
            console.error('响应状态:', error.response.status);
            console.error('响应数据:', error.response.data);
        }
        ElMessage.error(error.message || '保存计价记录失败');
    } finally {
        savingRecord.value = false;
    }
};

// 监听 results 变化，自动保存检测记录
watch(results, (newValue) => {
    if (newValue) {
        savePricingRecord();
    }
});

onMounted(() => {
    fetchPriceDatabase();
});
</script>

<style scoped>
.container {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
}

h1 {
    text-align: center;
    color: #2c3e50;
    margin-bottom: 2rem;
}

.upload-box {
    border: 2px dashed #ccc;
    border-radius: 8px;
    padding: 2rem;
    text-align: center;
    margin-bottom: 2rem;
}

.upload-btn {
    background: #409eff;
    color: white;
    padding: 12px 24px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    transition: background 0.3s;
    margin: 5px;
}

.upload-btn:hover {
    background: #66b1ff;
}

.preview {
    margin-top: 1rem;
}

.results {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 1.5rem;
    margin-top: 2rem;
}

.detection-time {
    margin-bottom: 1rem;
    color: #666;
}

.result-list {
    margin: 1rem 0;
}

.result-item {
    display: flex;
    justify-content: space-between;
    padding: 12px;
    border-bottom: 1px solid #eee;
}

.total-price {
    text-align: right;
    font-size: 1.2rem;
    font-weight: bold;
    color: #67c23a;
    margin-top: 1rem;
}

.error-message {
    color: #f56c6c;
    padding: 1rem;
    background: #fef0f0;
    border-radius: 4px;
    margin-top: 1rem;
}

.save-button-container {
    margin-top: 20px;
    display: flex;
    justify-content: center;
}

.el-button {
    border-radius: 8px;
    transition: all 0.3s;
    padding: 12px 25px;
}

.el-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
</style>
