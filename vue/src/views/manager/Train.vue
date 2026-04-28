<!--
*@
*@author Feiqi
*@date 2025/3/25 12:38
-->
<template>
    <div class="container">
        <h2>模型训练管理</h2>

        <!-- 选择模型 -->
        <div class="select-container">
            <label for="modelSelect">选择模型：</label>
            <el-select style="margin-right: 5px" v-model="selectedModel" placeholder="请选择模型" class="model-select">
                <el-option v-for="model in models" :key="model" :label="model" :value="model"></el-option>
            </el-select>
            <el-button type="primary" @click="startTraining">启动训练</el-button>
        </div>

        <!-- 训练记录 -->
        <div v-if="trainingResults.length">
            <h3>{{ selectedModel }} 近期训练结果</h3>
            <div v-for="(result, index) in trainingResults" :key="index" class="result">
                <h4>训练时间：{{ result.timestamp }}</h4>
                <pre class="log">{{ result.log }}</pre>
                <div class="image-grid">
                    <img v-for="(img, imgIndex) in result.images" :key="imgIndex" :src="img" alt="训练图片"/>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import request from '../../utils/request.js'
export default {
    data() {
        return {
            models: ["GoogLeNet", "ResNet50", "AlexNet","EfficientNet","MobileNet"],
            selectedModel: "GoogLeNet",
            trainingResults: [],
            pollingInterval: null
        };
    },
    methods: {
        async startTraining() {
            try {
                const response = await request.post("/train", { model: this.selectedModel });

                if (response.data.success) {
                    this.$message.success(response.data.message);
                    this.startPolling(); // 启动轮询获取最新结果
                } else {
                    this.$message.error(response.data.message);
                }
            } catch (error) {
                this.$message.error("请求失败: " + error.message);
            }
        },
        startPolling() {
            this.pollingInterval = setInterval(async () => {
                await this.fetchTrainingResults();
            }, 5000); // 每5秒刷新一次
        },
        async fetchTrainingResults() {
            try {
                const response = await request.get('/train/results', {
                    params: {model: this.selectedModel}
                });
                this.trainingResults = [{
                    timestamp: new Date(response.data.lastModified).toLocaleString(),
                    log: response.data.logs.join("\n"),
                    images: response.data.images
                }];
            } catch (error) {
                console.error("获取训练结果失败:", error);
            }
        }
    },
    beforeUnmount() {
        clearInterval(this.pollingInterval); // 清除轮询
    }
};
</script>

<style scoped>
.container {
    max-width: 800px;
    margin: auto;
    text-align: center;
}

.select-container {
    margin-bottom: 20px;
}

.result {
    border: 1px solid #ccc;
    padding: 15px;
    margin-bottom: 20px;
}

.log {
    background: #f4f4f4;
    padding: 10px;
    text-align: left;
    white-space: pre-wrap;
}

.image-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    margin-top: 10px;
}

.image-grid img {
    width: 100%;
    height: auto;
    border: 1px solid #ddd;
}
</style>
