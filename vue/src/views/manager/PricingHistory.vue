<template>
    <div class="container">
        <h1>计价历史记录</h1>

        <el-dialog title="删除确认" v-model="deleteDialogVisible" width="30%">
            <span>确定要删除这条计价记录吗？删除后不可恢复。</span>
            <template #footer>
                <el-button @click="deleteDialogVisible = false">取消</el-button>
                <el-button type="primary" @click="confirmDelete">确定删除</el-button>
            </template>
        </el-dialog>

        <div v-if="loading" class="loading">
            <el-skeleton :rows="10" animated />
        </div>

        <div v-else-if="!records.length" class="empty-records">
            <el-empty description="暂无检测记录" />
        </div>

        <div v-else class="records-list">
            <el-card v-for="record in records" :key="record.id" class="record-card" shadow="hover">
                <div class="record-header">
                    <div class="delete-btn">
                        <el-button
                            type="text"
                            icon="Delete"
                            @click="openDeleteDialog(record.id)"
                            class="text-danger"
                        >
                            删除
                        </el-button>
                    </div>
                    <div class="record-time">
                        <el-icon><Calendar /></el-icon>
                        {{ formatDate(record.createTime) }}
                    </div>
                    <div class="record-price">
                        <el-icon><Money /></el-icon>
                        总价: ¥{{ formatNumber(record.totalPrice) }}
                    </div>
                </div>

                <div class="record-content">
                    <div class="record-image">
                        <el-image
                            :src="imageSrc(record.imagePath)"
                            fit="cover"
                            :preview-src-list="[imageSrc(record.imagePath)]"
                            preview-teleported
                        />
                    </div>

                    <div class="record-details">
                        <div class="record-stats">
                            <el-statistic title="检测用时" :value="formatNumber(record.detectionDuration)" suffix="ms" />
                            <el-statistic title="运行时长" :value="formatNumber(record.executeDuration)" suffix="s" />
                            <el-statistic title="商品总数" :value="record.itemCount" />
                        </div>

                        <el-divider>商品明细</el-divider>

                        <div class="record-items">
                            <el-table :data="record.items || []" stripe>
                                <el-table-column prop="name" label="商品名称" />
                                <el-table-column prop="count" label="数量" width="100" />
                                <el-table-column prop="price" label="单价(¥)" width="100">
                                    <template #default="scope">
                                        {{ formatNumber(scope.row.price) }}
                                    </template>
                                </el-table-column>
                                <el-table-column label="小计(¥)" width="100">
                                    <template #default="scope">
                                        {{ formatNumber(scope.row.price * scope.row.count) }}
                                    </template>
                                </el-table-column>
                            </el-table>
                        </div>
                    </div>
                </div>
            </el-card>
        </div>
    </div>
</template>

<script setup>
import { ref, onActivated, onBeforeUnmount, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { Calendar, Money } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import request from '../../utils/request';
import { assetUrl } from '../../utils/config';

const route = useRoute();

const records = ref([]);
const loading = ref(true);
const deleteDialogVisible = ref(false);
const currentDeleteId = ref('');

function imageSrc(path) {
    return path ? assetUrl(path) : '';
}

const fetchRecords = async () => {
    try {
        loading.value = true;
        const response = await request.get('/pricingRecord/page', {
            params: {
                pageNum: 1,
                pageSize: 20,
                _t: Date.now()
            }
        });

        if (response.code === '200') {
            records.value = response.data?.list || [];
            return;
        }

        throw new Error(response.msg || '获取记录失败');
    } catch (error) {
        console.error('获取计价历史记录失败:', error);
        ElMessage.error(`获取历史记录失败：${error.message || '未知错误'}`);
        records.value = [];
    } finally {
        loading.value = false;
    }
};

const refreshIfCurrentPage = () => {
    if (route.path === '/pricing-history' && !document.hidden) {
        fetchRecords();
    }
};

const openDeleteDialog = (id) => {
    currentDeleteId.value = id;
    deleteDialogVisible.value = true;
};

const confirmDelete = async () => {
    try {
        const response = await request.delete(`/pricingRecord/${currentDeleteId.value}`);
        if (response.code === '200') {
            ElMessage.success('删除成功');
            await fetchRecords();
        } else {
            throw new Error(response.msg || '删除失败');
        }
    } catch (error) {
        console.error('删除记录失败:', error);
        ElMessage.error(`删除失败：${error.message || '未知错误'}`);
    } finally {
        deleteDialogVisible.value = false;
        currentDeleteId.value = '';
    }
};

const formatDate = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleString();
};

const formatNumber = (num) => {
    return Number.isFinite(Number(num)) ? Number(num).toFixed(2) : '0.00';
};

onMounted(() => {
    fetchRecords();
    window.addEventListener('focus', refreshIfCurrentPage);
    document.addEventListener('visibilitychange', refreshIfCurrentPage);
});

onActivated(fetchRecords);

watch(
    () => route.fullPath,
    () => {
        if (route.path === '/pricing-history') {
            fetchRecords();
        }
    }
);

onBeforeUnmount(() => {
    window.removeEventListener('focus', refreshIfCurrentPage);
    document.removeEventListener('visibilitychange', refreshIfCurrentPage);
});
</script>

<style scoped>
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

h1 {
    text-align: center;
    margin-bottom: 2rem;
    color: #2c3e50;
}

.loading, .empty-records {
    margin: 2rem 0;
}

.records-list {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.record-card {
    border-radius: 8px;
    overflow: hidden;
}

.record-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #eee;
}

.delete-btn {
    margin-right: auto;
}

.text-danger {
    color: #f56c6c;
    &:hover {
        color: #e63946;
        background-color: #fff5f5;
    }
}

.record-time, .record-price {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.record-price {
    font-weight: bold;
    color: #67c23a;
}

.record-content {
    display: flex;
    gap: 1.5rem;
    margin-top: 1rem;
}

.record-image {
    width: 300px;
    height: 250px;
    overflow: hidden;
    border-radius: 4px;
    .el-image {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
}

.record-details {
    flex: 1;
}

.record-stats {
    display: flex;
    justify-content: space-around;
    margin-bottom: 1rem;
}

.record-items {
    margin-top: 1rem;
}

@media (max-width: 768px) {
    .record-content {
        flex-direction: column;
    }
    .record-image {
        width: 100%;
        height: 200px;
    }
}
</style>
