<!--
*@
*@author Feiqi
*@date 2025/3/6 17:33
-->
<template>
    <div class="home-page">
        <div class="dashboard-container">
            <!-- 系统信息卡片 -->
            <div class="info-card system-intro">
                <div class="card-header">
                    <el-icon class="card-icon">
                        <ShoppingBag/>
                    </el-icon>
                    <h2>商品计价系统</h2>
                </div>
                <div class="card-content">
                    <p style="font-family: 'Microsoft YaHei',serif; font-size: 20px">基于深度学习的多目标检测商品计价系统，支持多商品同时识别和自动计价。</p>
                    <div class="system-stats">
                        <div class="stat-item">
                            <div class="stat-value">200</div>
                            <div class="stat-label">商品种类</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">17</div>
                            <div class="stat-label">商品大类</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">53739</div>
                            <div class="stat-label">训练图片</div>
                        </div>
                    </div>
                    <h2 align="center" style="font-size: 24px">测试图片展示</h2>
                    <div style="display: flex;margin-left: 20px; grid-template-columns: repeat(2, 1fr); grid-template-rows: repeat(2, 1fr); gap: 80px;">
                        <el-image
                                v-for="(item, index) in randomImgList"
                                :key="index"
                                :preview-src-list="[item]"
                                :src="item"
                                class="product-image hover-zoom-image"
                                fit="cover"
                                preview-teleported
                                style="width: 300px; height: 300px;border-radius: 10px;padding: 10px"
                        />
                    </div>
                </div>

                <!-- 热门商品卡片 -->
                <div class="card-header">
                    <el-icon class="card-icon">
                        <Star/>
                    </el-icon>
                    <h2>热门商品</h2>
                </div>
                <div class="card-content">
                    <div class="products-list">
                        <div v-for="(product, index) in topProducts" :key="index" class="product-item">
                            <div class="product-rank">{{ index + 1 }}</div>
                            <div class="product-info">
                                <div class="product-name">{{ product.name }}</div>
                                <div class="product-sales">销量: {{ product.sales }}</div>
                            </div>
                            <el-progress
                                    :color="getColorForRank(index)"
                                    :percentage="(product.sales / topProducts[0].sales) * 100"
                                    :show-text="false"
                                    :stroke-width="8"
                            />
                        </div>
                    </div>
                </div>
            </div>

            <!-- 销售统计卡片 -->
            <div class="info-card sales-chart">
                <div class="card-header">
                    <el-icon class="card-icon">
                        <TrendCharts/>
                    </el-icon>
                    <h2>商品销售量</h2>
                </div>
                <div ref="salesChartContainer" class="sales-chart-container"></div>

                <!-- 数据分布卡片 -->
                <div class="card-header">
                    <el-icon class="card-icon">
                        <DataAnalysis/>
                    </el-icon>
                    <h2>销售分布</h2>
                </div>
                <div ref="pieChartContainer" class="pie-chart-container"></div>
            </div>
        </div>

        <!-- 数据集展示区 -->
        <div class="dataset-section">
            <div class="section-header">
                <h2>数据集介绍</h2>
            </div>
            <div class="dataset-content">
                <div class="dataset-description">
                    <p style="font-size: 19px">本项目使用的数据集为RPC（retail_product_checkout）数据集，包含200种商品，属于17个商品大类（如方便面、纸巾、饮料等），天然构成了层次的结构。数据集中分为训练集，验证集和测试集，其中训练集内的商品图像为单品图，验证集和测试集内的图像为多品图，即一张图内包含多个多种商品。模型在单品图上进行训练，并在多品图上验证和测试。该数据集较为模拟真实购买场景，无论商品类别、商品个数、摆放角度及遮挡等等因素均接近实际零售场景。</p>
                </div>
                <div class="dataset-images">
                    <img alt="数据集样例" class="sample-image" src="/sample.png">
                </div>
            </div>
            <div align="center" style="margin-top: 50px;margin-bottom: -60px">
                <h2>测试集数据展示</h2>
            </div>
            <div ref="chartContainer" style="height: 600px"></div>
        </div>

        <!-- 加载和错误状态 -->
        <div v-if="loading" class="status-message loading">数据加载中...</div>
    </div>
</template>

<script setup>
import {nextTick, onBeforeUnmount, onMounted, ref} from 'vue';
import * as echarts from 'echarts';
import {DataAnalysis, ShoppingBag, Star, TrendCharts} from '@element-plus/icons-vue';
import request from '../../utils/request';

// 图表相关引用
const chartContainer = ref(null);
let chartInstance = null;
const pieChartContainer = ref(null);
let pieChartInstance = null;
const salesChartContainer = ref(null);
let salesChartInstance = null;
const imgList = ref([]);
const randomImgList = ref([]);
// 状态管理
const loading = ref(true);
const error = ref(false);
const products = ref([]);


// 热门商品数据
const topProducts = ref([]);

// 获取排名对应的颜色
const getColorForRank = (index) => {
    const colors = ['#f56c6c', '#e6a23c', '#409eff', '#67c23a', '#909399'];
    return colors[index] || colors[4];
};

// 禁止页面回退
history.pushState(null, null, document.URL);
window.addEventListener('popstate', () => {
    history.pushState(null, null, document.URL);
});

// 数据获取
const fetchData = async () => {
    try {
        const response = await fetch('/image_stats.txt');
        if (!response.ok) throw new Error(`HTTP错误! 状态码: ${response.status}`);
        const text = await response.text();
        return text.trim().split('\n').map(line => {
            const [name, value] = line.split(':');
            return {name, value: parseInt(value)};
        });
    } catch (err) {
        console.error('数据获取失败:', err);
        error.value = true;
        return [];
    } finally {
        loading.value = false;
    }
};

// 初始化销售量图表
const initSalesChart = async () => {
    if (salesChartInstance) {
        salesChartInstance.dispose();
    }

    try {
        // 从数据库获取商品销售量数据
        const response = await request.get('/product/sales');
        if (response.code !== '200') {
            throw new Error(response.msg || '获取销售数据失败');
        }

        // 处理销售数据
        const salesData = response.data || [];

        // 排序销售数据（可选）
        salesData.sort((a, b) => b.sales - a.sales);

        // 取前7个商品展示
        const topSalesData = salesData.slice(0, 7);

        salesChartInstance = echarts.init(salesChartContainer.value);
        const option = {
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'shadow'
                },
                formatter: '{b}: {c} 件'
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            },
            xAxis: {
                type: 'category',
                data: topSalesData.map(item => item.name),
                axisLine: {
                    lineStyle: {
                        color: '#ddd'
                    }
                },
                axisTick: {
                    show: false
                },
                axisLabel: {
                    rotate: topSalesData.length > 5 ? 30 : 0,
                    formatter: function (value) {
                        if (value.length > 6) {
                            return value.substring(0, 6) + '...';
                        }
                        return value;
                    }
                }
            },
            yAxis: {
                type: 'value',
                name: '销售量',
                axisLine: {
                    show: false
                },
                axisTick: {
                    show: false
                },
                splitLine: {
                    lineStyle: {
                        color: '#f5f5f5'
                    }
                }
            },
            series: [{
                name: '销售量',
                type: 'bar',
                data: topSalesData.map(item => item.sales || 0),
                barWidth: '40%',
                itemStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        {offset: 0, color: '#4b6cb7'},
                        {offset: 1, color: '#182848'}
                    ]),
                    borderRadius: [4, 4, 0, 0]
                },
                emphasis: {
                    itemStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            {offset: 0, color: '#5d7dcb'},
                            {offset: 1, color: '#243b6a'}
                        ])
                    }
                },
                label: {
                    show: true,
                    position: 'top',
                    color: '#666'
                }
            }]
        };

        salesChartInstance.setOption(option);
    } catch (err) {
        console.error('获取销售数据失败:', err);
        error.value = true;
    }

    window.addEventListener('resize', () => salesChartInstance.resize());
};

// 初始化热门商品列表
const initTopProducts = async () => {
    try {
        // 从数据库获取商品销售量数据
        const response = await request.get('/product/sales');
        if (response.code !== '200') {
            throw new Error(response.msg || '获取销售数据失败');
        }

        // 处理销售数据
        const salesData = response.data || [];

        // 按销量排序
        salesData.sort((a, b) => b.sales - a.sales);

        // 取前5个作为热门商品
        topProducts.value = salesData.slice(0, 5).map(item => ({
            name: item.name,
            sales: item.sales || 0
        }));

    } catch (err) {
        console.error('获取热门商品数据失败:', err);
    }
};

// 初始化饼图
const initPieChart = async () => {
    if (pieChartInstance) {
        pieChartInstance.dispose();
    }

    try {
        // 从数据库获取商品销售量数据
        const response = await request.get('/product/sales/category');
        if (response.code !== '200') {
            throw new Error(response.msg || '获取销售分类数据失败');
        }

        // 处理销售分类数据
        let categoryData = response.data || [];

        // 按销量排序
        categoryData.sort((a, b) => b.value - a.value);

        // 取前10个分类
        categoryData = categoryData.slice(0, 10);

        pieChartInstance = echarts.init(pieChartContainer.value);
        const option = {
            tooltip: {
                trigger: 'item',
                formatter: '{b}: {c} ({d}%)'
            },
            legend: {
                type: 'scroll',
                orient: 'vertical',
                right: 10,
                top: 'center',
                itemWidth: 10,
                itemHeight: 10,
                textStyle: {
                    fontSize: 12
                },
                formatter: function (name) {
                    return name;
                }
            },
            series: [
                {
                    type: 'pie',
                    radius: '65%',
                    center: ['40%', '50%'],
                    data: categoryData,
                    emphasis: {
                        itemStyle: {
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }
                    },
                    label: {
                        show: true,
                        position: 'outside',
                        formatter: '{b}',
                        textStyle: {
                            fontSize: 11
                        },
                        alignTo: 'edge',
                        edgeDistance: 10
                    },
                    labelLine: {
                        length: 10,
                        length2: 10,
                        smooth: true
                    },
                    labelLayout: {
                        hideOverlap: true
                    },
                    itemStyle: {
                        borderRadius: 5,
                        borderColor: '#fff',
                        borderWidth: 2
                    }
                }
            ],
            color: ['#4b6cb7', '#3F99EF', '#36CBCB', '#4ECB73', '#FBD437', '#F6C044', '#FF6B6B', '#9F8FEF', '#4EA8DE', '#F091A9']
        };

        pieChartInstance.setOption(option);
    } catch (err) {
        console.error('获取销售分类数据失败:', err);
        pieChartInstance = echarts.init(pieChartContainer.value);
        const option = {
            tooltip: {
                trigger: 'item',
                formatter: '{b}: {c} ({d}%)'
            },
            legend: {
                type: 'scroll',
                orient: 'vertical',
                right: 10,
                top: 'center',
                itemWidth: 10,
                itemHeight: 10,
                textStyle: {
                    fontSize: 12
                },
                formatter: function (name) {
                    return name;
                }
            },
            series: [
                {
                    type: 'pie',
                    radius: '65%',
                    center: ['40%', '50%'],
                    data: categoryData,
                    emphasis: {
                        itemStyle: {
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }
                    },
                    label: {
                        show: true,
                        position: 'outside',
                        formatter: '{b}',
                        textStyle: {
                            fontSize: 11
                        },
                        alignTo: 'edge',
                        edgeDistance: 10
                    },
                    labelLine: {
                        length: 10,
                        length2: 10,
                        smooth: true
                    },
                    labelLayout: {
                        hideOverlap: true
                    },
                    itemStyle: {
                        borderRadius: 5,
                        borderColor: '#fff',
                        borderWidth: 2
                    }
                }
            ],
            color: ['#4b6cb7', '#3F99EF', '#36CBCB', '#4ECB73', '#FBD437', '#F6C044', '#FF6B6B', '#9F8FEF', '#4EA8DE', '#F091A9']
        };

        pieChartInstance.setOption(option);
    }

    window.addEventListener('resize', () => pieChartInstance.resize());
};

// 图表初始化
const initChart = async () => {
    const data = await fetchData();
    if (data.length === 0) return;
    products.value = data;

    // 原有的数据集图表初始化代码...
    if (chartInstance) {
        chartInstance.dispose();
    }
    chartInstance = echarts.init(chartContainer.value);
    const option = {
        tooltip: {
            trigger: 'axis',
            formatter: params => {
                const data = params[0];
                return `${data.name}<br/>数量：${data.value}`;
            }
        },
        xAxis: {
            type: 'category',
            data: products.value.map(item => item.name),
            axisLabel: {
                formatter: value => value.slice(0, 6) + (value.length > 6 ? '...' : ''),
                rich: {
                    full: {
                        width: 120,
                        overflow: 'break',
                        fontSize: 12
                    }
                }
            }
        },
        yAxis: {
            type: 'value',
            axisLabel: {
                formatter: value => `${value}张`
            }
        },
        dataZoom: [{
            type: 'slider',
            xAxisIndex: 0,
            start: 0,
            end: 15,
            bottom: 30,
            height: 20,
            brushSelect: false
        }],
        series: [{
            type: 'bar',
            data: products.value,
            barWidth: '55%',
            label: {
                show: true,
                position: 'top',
                formatter: '{c}',
                color: '#2c3e50',
                fontSize: 12,
                padding: [3, 5],
                overflow: 'break',
                width: 80,
            },
            itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    {offset: 0, color: '#36D1DC'},
                    {offset: 1, color: '#5B86E5'}
                ])
            },
            emphasis: {
                itemStyle: {
                    shadowBlur: 10,
                    shadowColor: 'rgba(0, 0, 0, 0.3)'
                }
            },
            progressive: 400,
            animationThreshold: 400
        }]
    };
    chartInstance.setOption(option);
    // 动态标签显示优化
    chartInstance.on('mouseover', 'series', (params) => {
        chartInstance.setOption({
            xAxis: {
                axisLabel: {
                    formatter: (value, index) =>
                            index === params.dataIndex ?
                                    '{full|' + value + '}' :
                                    value.slice(0, 6) + (value.length > 6 ? '...' : '')
                }
            }
        });
    });
    window.addEventListener('resize', () => chartInstance.resize());
};
// 获取随机2张图片
const getRandomImages = () => {
    const allImages = [...imgList.value];
    const randomImages = [];
    const imageCount = Math.min(2, allImages.length);
    for (let i = 0; i < imageCount; i++) {
        const randomIndex = Math.floor(Math.random() * allImages.length);
        randomImages.push(allImages[randomIndex]);
        allImages.splice(randomIndex, 1);
    }
    randomImgList.value = randomImages;
};

onMounted(async () => {
    // 初始化所有图表
    await nextTick();
    loading.value = true;
    try {
        await initSalesChart();
        await initTopProducts();
        await initPieChart();
        await initChart();
    } catch (err) {
        console.error('初始化图表失败:', err);
        error.value = true;
    } finally {
        loading.value = false;
    }
    const imageModules = import.meta.glob('/src/test/images/*.{jpg,jpeg}', {eager: true});
    const imagePaths = Object.values(imageModules).map(module => module.default);
    imgList.value = imagePaths;
    getRandomImages();
});

onBeforeUnmount(() => {
    if (chartInstance) chartInstance.dispose();
    if (pieChartInstance) pieChartInstance.dispose();
    if (salesChartInstance) salesChartInstance.dispose();

    window.removeEventListener('resize', () => {
        if (chartInstance) chartInstance.resize();
        if (pieChartInstance) pieChartInstance.resize();
        if (salesChartInstance) salesChartInstance.resize();
    });
});
</script>

<style scoped>
.home-page {
    padding: 20px;
    background-color: #f5f7fa;
}

.dashboard-container {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: auto auto;
    gap: 20px;
    margin-bottom: 25px;
}

.info-card {
    background-color: #fff;
    border-radius: 10px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
    padding: 20px;
    height: 100%;
    display: flex;
    flex-direction: column;
    transition: transform 0.3s, box-shadow 0.3s;
}

.info-card:hover {
    transform: translateY(-10px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.card-header {
    display: flex;
    align-items: center;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 1px solid #f0f0f0;
}

.card-icon {
    font-size: 24px;
    margin-right: 10px;
    color: #4b6cb7;
}

.card-header h2 {
    font-size: 18px;
    font-weight: 500;
    margin: 0;
    color: #333;
}

.card-content {
    flex: 1;
}

/* 系统介绍卡片 */
.system-intro p {
    color: #666;
    line-height: 1.6;
    margin-bottom: 20px;
}

.system-stats {
    display: flex;
    justify-content: space-between;
    margin-top: 20px;
}

.stat-item {
    text-align: center;
    padding: 10px;
    border-radius: 8px;
    background-color: #f8f9fa;
}

.stat-value {
    font-size: 24px;
    font-weight: 600;
    color: #4b6cb7;
    margin-bottom: 5px;
}

.stat-label {
    font-size: 14px;
    color: #888;
}

/* 图表容器 */
.sales-chart-container,
.pie-chart-container {
    height: 300px;
    width: 100%;
}

/* 热门商品列表 */
.products-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.product-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 5px 0;
}

.product-rank {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 14px;
    color: white;
    background-color: #909399;
}

.product-item:nth-child(1) .product-rank {
    background-color: #f56c6c;
}

.product-item:nth-child(2) .product-rank {
    background-color: #e6a23c;
}

.product-item:nth-child(3) .product-rank {
    background-color: #409eff;
}

.product-info {
    flex: 1;
    margin-right: 10px;
}

.product-name {
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 3px;
}

.product-sales {
    font-size: 12px;
    color: #999;
}

/* 数据集部分 */
.dataset-section {
    background-color: #fff;
    border-radius: 10px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
    padding: 20px;
    margin-bottom: 25px;
}

.section-header h2 {
    font-size: 18px;
    font-weight: 500;
    margin: 0 0 15px;
    color: #333;
    display: flex;
    align-items: center;
}

.dataset-content {
    display: flex;
    gap: 20px;
}

.dataset-description {
    flex: 1;
}

.dataset-description p {
    color: #666;
    line-height: 1.6;
    margin: 0;
}

.dataset-images {
    width: 40%;
    display: flex;
    justify-content: center;
    align-items: center;
}

.sample-image {
    max-width: 100%;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 加载和错误状态 */
.status-message {
    text-align: center;
    padding: 20px;
    font-size: 16px;
    border-radius: 8px;
    margin-top: 20px;
}

.loading {
    background-color: #e6f7ff;
    color: #1890ff;
}

.error {
    background-color: #fff2f0;
    color: #ff4d4f;
}

/* 响应式调整 */
@media (max-width: 1200px) {
    .dashboard-container {
        grid-template-columns: 1fr;
    }

    .dataset-content {
        flex-direction: column;
    }

    .dataset-images {
        width: 100%;
    }
}
</style>
