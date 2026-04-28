<!--
*@
*@author Feiqi
*@date 2025/4/1 11:09
-->
<template>
    <div>
        <!-- 选择模型 -->
        <el-select v-model="selectedModel" placeholder="请选择模型" @change="fetchTrainingLog">
            <el-option
                    v-for="model in models"
                    :key="model"
                    :label="model"
                    :value="model"
            >
            </el-option>
            <el-option label="结果对比" value="modelComparison"></el-option>
        </el-select>

        <!-- 单个模型的日志表格 -->
        <el-table v-if="selectedModel!== 'modelComparison' && trainingLog.length > 0" :data="trainingLog" stripe>
            <el-table-column label="Epoch" prop="epoch"></el-table-column>
            <el-table-column label="训练时间">
                <template #header>训练时间/s</template>
                <template #default="scope">
                    {{ scope.row.time.train }}
                </template>
            </el-table-column>
            <el-table-column label="验证时间">
                <template #header>验证时间/s</template>
                <template #default="scope">
                    {{ scope.row.time.val }}
                </template>
            </el-table-column>
            <el-table-column label="训练损失">
                <template #header>训练损失</template>
                <template #default="scope">
                    {{ scope.row.train.loss }}
                </template>
            </el-table-column>
            <el-table-column label="训练准确率">
                <template #header>训练准确率/%</template>
                <template #default="scope">
                    {{ (scope.row.train.precision * 100).toFixed(2) }}%
                </template>
            </el-table-column>
            <el-table-column label="验证损失">
                <template #header>验证损失</template>
                <template #default="scope">
                    {{ scope.row.val.loss }}
                </template>
            </el-table-column>
            <el-table-column label="验证准确率">
                <template #header>验证准确率/%</template>
                <template #default="scope">
                    {{ (scope.row.val.precision * 100).toFixed(2) }}%
                </template>
            </el-table-column>
        </el-table>
        <hr>
        <!-- 单个模型的数值曲线图 -->
        <div v-if="selectedModel!== 'modelComparison'" ref="singleChartRef" style="width: 100%; height: 400px;"></div>

        <!-- 模型结果对比表格 -->
        <el-table v-if="selectedModel === 'modelComparison'" :data="comparisonTableData" stripe>
            <el-table-column label="模型" prop="model"></el-table-column>
            <el-table-column label="训练损失平均值" prop="trainLoss"></el-table-column>
            <el-table-column label="验证损失平均值" prop="valLoss"></el-table-column>
            <el-table-column label="训练准确率平均值/%" prop="trainPre"></el-table-column>
            <el-table-column label="验证准确率平均值/%" prop="valPre"></el-table-column>
        </el-table>
        <!-- 模型指标进度条对比 -->
        <div v-if="selectedModel === 'modelComparison'" class="progress-table-wrapper">
            <table class="progress-table">
                <thead>
                <tr>
                    <th>模型</th>
                    <th>Precision</th>
                    <th>Accuracy</th>
                    <th>Recall</th>
                    <th>F1-score</th>
                </tr>
                </thead>
                <tbody>
                <tr v-for="model in modelNames" :key="model">
                    <td>{{ model }}</td>
                    <td>
                        <div :class="{ best: isBest('valPrecision', model) }" class="progress-bar-cell">
                            <div :style="{ width: getMetric(model, 'valPrecision') + '%' }" class="progress-bar-inner">
                                <span class="progress-bar-text">{{ getMetric(model, 'valPrecision') }}%</span>
                            </div>
                        </div>
                    </td>
                    <td>
                        <div :class="{ best: isBest('valAcc', model) }" class="progress-bar-cell">
                            <div :style="{ width: getMetric(model, 'valAcc') + '%' }" class="progress-bar-inner">
                                <span class="progress-bar-text">{{ getMetric(model, 'valAcc') }}%</span>
                            </div>
                        </div>
                    </td>
                    <td>
                        <div :class="{ best: isBest('valRecall', model) }" class="progress-bar-cell">
                            <div :style="{ width: getMetric(model, 'valRecall') + '%' }" class="progress-bar-inner">
                                <span class="progress-bar-text">{{ getMetric(model, 'valRecall') }}%</span>
                            </div>
                        </div>
                    </td>
                    <td>
                        <div :class="{ best: isBest('valF1', model) }" class="progress-bar-cell">
                            <div :style="{ width: getMetric(model, 'valF1') + '%' }" class="progress-bar-inner">
                                <span class="progress-bar-text">{{ getMetric(model, 'valF1') }}%</span>
                            </div>
                        </div>
                    </td>
                </tr>
                </tbody>
            </table>
        </div>
        <!-- 模型结果对比图 -->
        <div v-if="selectedModel === 'modelComparison'" ref="comparisonChartRef" style="width: 100%; height: 400px;"></div>
    </div>
</template>

<script setup>
import {computed, onMounted, ref, watch} from 'vue';
import * as echarts from 'echarts';
import {ElOption, ElSelect, ElTable, ElTableColumn} from 'element-plus';
import request from '../../utils/request.js'
// 模型列表
const models = ['AlexNet', 'EfficientNet', 'GoogLeNet', 'MobileNet', 'ResNet50', 'YOLOv8'];
// 选择的模型
const selectedModel = ref('AlexNet');
// 训练日志
const trainingLog = ref([]);
// 单个模型的图表引用
const singleChartRef = ref(null);
// 模型对比图表引用
const comparisonChartRef = ref(null);
// 4个指标进度条图表引用
const precisionChartRef = ref(null);
const accuracyChartRef = ref(null);
const recallChartRef = ref(null);
const f1ChartRef = ref(null);
// 所有模型的训练结果平均值
const allModelAverages = ref({});
// 模型对比表格数据
const comparisonTableData = ref([]);

// 获取训练结果
const fetchTrainingLog = async () => {
    if (selectedModel.value === 'modelComparison') {
        await updateComparisonChart();
        return;
    }
    try {
        const response = await request.get(`/files/training-log/${selectedModel.value}`);
        const data = response.data;
        trainingLog.value = JSON.parse(data);
        updateSingleChart();
    } catch (error) {
        console.error('Error fetching training log:', error);
    }
};

// 更新单个模型的图表
const updateSingleChart = () => {
    const chart = echarts.init(singleChartRef.value);
    const epochs = trainingLog.value.map(item => item.epoch);
    const trainLoss = trainingLog.value.map(item => item.train.loss);
    const valLoss = trainingLog.value.map(item => item.val.loss);
    const trainPre = trainingLog.value.map(item => item.train.precision * 100);
    const valPre = trainingLog.value.map(item => item.val.precision * 100);

    const option = {
        tooltip: {
            trigger: 'axis',
            formatter: function (params) {
                let result = params[0].name + '<br>';
                params.forEach((param) => {
                    if (param.seriesName.includes('准确率')) {
                        result += param.seriesName + ': ' + param.value.toFixed(2) + '%<br>';
                    } else {
                        result += param.seriesName + ': ' + param.value + '<br>';
                    }
                });
                return result;
            }
        },
        legend: {
            data: ['训练损失', '验证损失', '训练准确率', '验证准确率']
        },
        xAxis: {
            type: 'category',
            data: epochs
        },
        yAxis: {
            type: 'value',
            axisLabel: {
                formatter: function (value, index) {
                    if (index === 0) {
                        return value;
                    }
                    return value + '%';
                }
            }
        },
        series: [
            {
                name: '训练损失',
                type: 'line',
                data: trainLoss
            },
            {
                name: '验证损失',
                type: 'line',
                data: valLoss
            },
            {
                name: '训练准确率',
                type: 'line',
                data: trainPre
            },
            {
                name: '验证准确率',
                type: 'line',
                data: valPre
            }
        ]
    };

    chart.setOption(option);
};

// 计算模型训练结果的平均值
const calculateAverages = (log) => {
    const totalTrainLoss = log.reduce((sum, item) => sum + item.train.loss, 0);
    const totalValLoss = log.reduce((sum, item) => sum + item.val.loss, 0);
    const totalTrainPre = log.reduce((sum, item) => sum + item.train.precision, 0);
    const totalValPre = log.reduce((sum, item) => sum + item.val.precision, 0);
    const totalValAcc = log.reduce((sum, item) => sum + (item.val.acc || 0), 0);
    const totalValRecall = log.reduce((sum, item) => sum + (item.val.recall || 0), 0);
    const totalValF1 = log.reduce((sum, item) => sum + (item.val.f1 || 0), 0);
    const totalValPrecision = log.reduce((sum, item) => sum + (item.val.precision || 0), 0);
    const numEpochs = log.length;
    return {
        trainLoss: (totalTrainLoss / numEpochs).toFixed(2),
        valLoss: (totalValLoss / numEpochs).toFixed(2),
        trainPre: (totalTrainPre / numEpochs * 100).toFixed(2),
        valPre: (totalValPre / numEpochs * 100).toFixed(2),
        valAcc: (totalValAcc / numEpochs * 100).toFixed(2),
        valRecall: (totalValRecall / numEpochs * 100).toFixed(2),
        valF1: (totalValF1 / numEpochs * 100).toFixed(2),
        valPrecision: (totalValPrecision / numEpochs * 100).toFixed(2)
    };
};

// 更新模型结果对比图
const updateComparisonChart = async () => {
    for (const model of models) {
        try {
            const response = await request.get(`/files/training-log/${model}`);
            const data = response.data
            const log = JSON.parse(data);
            allModelAverages.value[model] = calculateAverages(log);
        } catch (error) {
            console.error(`Error fetching training log for ${model}:`, error);
        }
    }

    // 生成表格数据
    comparisonTableData.value = Object.entries(allModelAverages.value).map(([model, averages]) => ({
        model,
        trainLoss: averages.trainLoss,
        valLoss: averages.valLoss,
        trainPre: averages.trainPre + '%',
        valPre: averages.valPre + '%'
    }));

    const chart = echarts.init(comparisonChartRef.value);
    const modelNames = Object.keys(allModelAverages.value);
    const trainLossAverages = modelNames.map(model => parseFloat(allModelAverages.value[model].trainLoss));
    const valLossAverages = modelNames.map(model => parseFloat(allModelAverages.value[model].valLoss));
    const trainPreAverages = modelNames.map(model => parseFloat(allModelAverages.value[model].trainPre));
    const valPreAverages = modelNames.map(model => parseFloat(allModelAverages.value[model].valPre));

    const option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross',
                crossStyle: {
                    color: '#999'
                }
            },
            formatter: function (params) {
                let result = params[0].name + '<br>';
                params.forEach((param) => {
                    if (param.seriesName.includes('准确率')) {
                        result += param.seriesName + ': ' + param.value.toFixed(2) + '%<br>';
                    } else {
                        result += param.seriesName + ': ' + param.value.toFixed(2) + '<br>';
                    }
                });
                return result;
            }
        },
        legend: {
            data: ['训练损失平均值', '验证损失平均值', '训练准确率平均值', '验证准确率平均值']
        },
        xAxis: {
            type: 'category',
            data: modelNames
        },
        // 两个 yAxis，分别对应损失值和准确率值
        yAxis: [
            {
                type: 'value',
                axisLabel: {
                    formatter: function (value) {
                        return value.toFixed(2);
                    }
                },
                name: '损失值'
            },
            {
                type: 'value',
                axisLabel: {
                    formatter: function (value) {
                        return value.toFixed(2) + '%';
                    }
                },
                name: '准确率'
            }
        ],
        series: [
            {
                name: '训练损失平均值',
                type: 'bar',
                data: trainLossAverages,
                // 对应第一个 yAxis（损失值轴）
                yAxisIndex: 0
            },
            {
                name: '验证损失平均值',
                type: 'bar',
                data: valLossAverages,
                yAxisIndex: 0
            },
            {
                name: '训练准确率平均值',
                type: 'bar',
                data: trainPreAverages,
                // 对应第二个 yAxis（准确率轴）
                yAxisIndex: 1
            },
            {
                name: '验证准确率平均值',
                type: 'bar',
                data: valPreAverages,
                yAxisIndex: 1
            }
        ]
    };
    chart.setOption(option);

    // 4个独立进度条图
    const metricMap = [
        {key: 'valPrecision', label: 'Precision', ref: precisionChartRef},
        {key: 'valAcc', label: 'Accuracy', ref: accuracyChartRef},
        {key: 'valRecall', label: 'Recall', ref: recallChartRef},
        {key: 'valF1', label: 'F1-score', ref: f1ChartRef}
    ];
    metricMap.forEach(metric => {
        const chart = echarts.init(metric.ref.value);
        const data = modelNames.map(model => parseFloat(allModelAverages.value[model][metric.key] || 0));
        const option = {
            tooltip: {
                trigger: 'axis',
                axisPointer: {type: 'shadow'},
                formatter: function (params) {
                    let res = params[0].name + '<br/>';
                    params.forEach(item => {
                        res += metric.label + ': ' + item.value.toFixed(2) + '%<br/>';
                    });
                    return res;
                }
            },
            title: {
                text: metric.label + ' 对比',
                left: 'left',
                top: 0,
                textStyle: {fontSize: 16}
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                top: 32,
                containLabel: true
            },
            xAxis: {
                type: 'value',
                max: 100,
                axisLabel: {
                    formatter: '{value}%'
                }
            },
            yAxis: {
                type: 'category',
                data: modelNames,
            },
            series: [
                {
                    name: metric.label,
                    type: 'bar',
                    barWidth: 20,
                    label: {
                        show: true,
                        position: 'right',
                        formatter: '{c}%'
                    },
                    data: data,
                    itemStyle: {
                        color: '#5470C6'
                    }
                }
            ]
        };
        chart.setOption(option);
    });
};

// 初始化
onMounted(() => {
    fetchTrainingLog();
});

// 监听模型选择变化
watch(selectedModel, () => {
    fetchTrainingLog();
});

// 进度条表格相关计算
const modelNames = computed(() => Object.keys(allModelAverages.value));
const getMetric = (model, metric) => {
    const val = allModelAverages.value[model]?.[metric];
    return val ? parseFloat(val).toFixed(2) : '0.00';
};
const bestMap = computed(() => {
    const result = {};
    const metrics = ['valPrecision', 'valAcc', 'valRecall', 'valF1'];
    metrics.forEach(metric => {
        let max = -Infinity;
        modelNames.value.forEach(model => {
            const v = parseFloat(allModelAverages.value[model]?.[metric] || 0);
            if (v > max) max = v;
        });
        result[metric] = max;
    });
    return result;
});
const isBest = (metric, model) => {
    return parseFloat(getMetric(model, metric)) === bestMap.value[metric];
};
</script>

<style scoped>
.progress-bar-row {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: flex-start;
    width: 100%;
    margin-top: 24px;
    gap: 16px;
}

.progress-bar-chart {
    width: 25%;
    min-width: 180px;
    height: 80px;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 24px;
    flex-direction: column;
}

.progress-table-wrapper {
    width: 100%;
    overflow-x: auto;
    margin: 32px 0 24px 0;
}

.progress-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0 8px;
    background: #fff;
}

.progress-table th, .progress-table td {
    text-align: center;
    padding: 8px 4px;
    min-width: 140px;
    width: 140px;
}

.progress-bar-cell {
    width: 100%;
    height: 24px;
    background: #f5f7fa;
    border-radius: 12px;
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
}

.progress-bar-inner {
    height: 100%;
    background: linear-gradient(90deg, #91caff 0%, #409eff 100%);
    border-radius: 12px;
    display: flex;
    align-items: center;
    transition: width 0.5s;
    position: relative;
}

.progress-bar-text {
    position: absolute;
    left: 50%;
    top: 0;
    transform: translateX(-50%);
    color: #333;
    font-size: 13px;
    font-weight: 500;
    z-index: 2;
}

.progress-bar-cell.best .progress-bar-inner {
    background: linear-gradient(90deg, #67c23a 0%, #409eff 100%);
    box-shadow: 0 0 8px #67c23a99;
}

.progress-bar-cell.best .progress-bar-text {
    color: #f2ce37;
    font-weight: bold;
}
</style>

