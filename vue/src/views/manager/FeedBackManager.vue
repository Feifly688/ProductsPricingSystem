<!--
*@
*@author Feiqi
*@date 2025/4/15 16:21
-->
<template>
    <div class="feedback-manage">
        <el-card>
            <template #header>
                <div class="card-header">
                    <span>用户反馈管理</span>
                    <div class="right">
                        <el-radio-group v-model="filterStatus" @change="handleFilterChange">
                            <el-radio-button :label="-1">全部</el-radio-button>
                            <el-radio-button :label="0">未读</el-radio-button>
                            <el-radio-button :label="1">已读</el-radio-button>
                        </el-radio-group>
                        <el-button class="refresh-btn" link type="primary" @click="loadFeedbackList">
                            <el-icon>
                                <Refresh/>
                            </el-icon>
                            刷新
                        </el-button>
                    </div>
                </div>
            </template>

            <el-table v-loading="loading" :data="filteredFeedbackList" style="width: 100%">
                <el-table-column label="用户名" prop="username" width="120"/>
                <el-table-column label="反馈内容" min-width="300" prop="content" show-overflow-tooltip>
                    <template #default="scope">
                        <div style="white-space: pre-wrap;">{{ scope.row.content }}</div>
                    </template>
                </el-table-column>
                <el-table-column label="提交时间" prop="createTime" width="160">
                    <template #default="scope">
                        {{ formatDate(scope.row.createTime) }}
                    </template>
                </el-table-column>
                <el-table-column label="状态" prop="status" width="100">
                    <template #default="scope">
                        <el-tag :type="scope.row.status === 1 ? 'success' : 'warning'">
                            {{ scope.row.status === 1 ? '已读' : '未读' }}
                        </el-tag>
                    </template>
                </el-table-column>
                <el-table-column fixed="right" label="操作" width="180">
                    <template #default="scope">
                        <el-button
                                v-if="scope.row.status === 0"
                                size="small"
                                type="primary"
                                @click="handleReply(scope.row)"
                        >
                            回复
                        </el-button>
                        <el-button
                                v-else
                                size="small"
                                type="info"
                                @click="handleViewReply(scope.row)"
                        >
                            查看回复
                        </el-button>
                        <el-popconfirm
                                title="确定要删除这条反馈吗？"
                                @confirm="handleDelete(scope.row)"
                        >
                            <template #reference>
                                <el-button
                                        size="small"
                                        type="danger"
                                >
                                    删除
                                </el-button>
                            </template>
                        </el-popconfirm>
                    </template>
                </el-table-column>
            </el-table>

            <!-- 分页 -->
            <div class="pagination-container">
                <el-pagination
                        v-model:current-page="currentPage"
                        v-model:page-size="pageSize"
                        :page-sizes="[10, 20, 50, 100]"
                        :total="total"
                        layout="total, sizes, prev, pager, next, jumper"
                        @size-change="handleSizeChange"
                        @current-change="handleCurrentChange"
                />
            </div>
        </el-card>

        <!-- 回复对话框 -->
        <el-dialog
                v-model="dialogVisible"
                :title="currentFeedback.status === 0 ? '回复反馈' : '查看反馈详情'"
                width="50%"
        >
            <el-form ref="replyFormRef" :model="replyForm" :rules="rules" label-width="80px">
                <el-form-item label="用户名">
                    <div class="info-text">{{ currentFeedback.username }}</div>
                </el-form-item>
                <el-form-item label="提交时间">
                    <div class="info-text">{{ formatDate(currentFeedback.createTime) }}</div>
                </el-form-item>
                <el-form-item label="反馈内容">
                    <div class="feedback-content">{{ currentFeedback.content }}</div>
                </el-form-item>
                <el-form-item label="回复内容" prop="reply">
                    <el-input
                            v-model="replyForm.reply"
                            :disabled="currentFeedback.status === 1"
                            :rows="4"
                            placeholder="请输入回复内容..."
                            type="textarea"
                    />
                </el-form-item>
                <el-form-item v-if="currentFeedback.status === 1" label="回复时间">
                    <div class="info-text">{{ formatDate(currentFeedback.replyTime) }}</div>
                </el-form-item>
            </el-form>
            <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">关闭</el-button>
          <el-button
                  v-if="currentFeedback.status === 0"
                  type="primary"
                  @click="submitReply"
          >
            提交回复
          </el-button>
        </span>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import {computed, onMounted, ref} from 'vue'
import {ElMessage} from 'element-plus'
import {Refresh} from '@element-plus/icons-vue'
import request from '../../utils/request'

const loading = ref(false)
const feedbackList = ref([])
const filterStatus = ref(-1)
const dialogVisible = ref(false)
const currentFeedback = ref({})
const replyForm = ref({
    reply: ''
})

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const rules = {
    reply: [
        {required: true, message: '请输入回复内容', trigger: 'blur'},
        {min: 1, max: 1000, message: '长度在 1 到 1000 个字符', trigger: 'blur'}
    ]
}

const replyFormRef = ref()

// 过滤后的反馈列表
const filteredFeedbackList = computed(() => {
    if (filterStatus.value === -1) {
        return feedbackList.value
    }
    return feedbackList.value.filter(item => item.status === filterStatus.value)
})

// 加载反馈列表
const loadFeedbackList = async () => {
    loading.value = true
    try {
        const res = await request.get('/feedback/list', {
            params: {
                role: '管理员'
            }
        })
        if (res.code === '200') {
            feedbackList.value = res.data || []
            total.value = feedbackList.value.length
        } else {
            throw new Error(res.msg || '加载失败')
        }
    } catch (error) {
        console.error('加载反馈列表失败:', error)
        ElMessage.error('加载反馈列表失败：' + error.message)
    } finally {
        loading.value = false
    }
}

// 处理回复
const handleReply = (row) => {
    currentFeedback.value = row
    replyForm.value.reply = ''
    dialogVisible.value = true
}

// 查看回复
const handleViewReply = (row) => {
    currentFeedback.value = row
    replyForm.value.reply = row.reply
    dialogVisible.value = true
}

// 提交回复
const submitReply = async () => {
    if (!replyFormRef.value) return

    await replyFormRef.value.validate(async (valid) => {
        if (valid) {
            try {
                const res = await request.put('/feedback/reply', {
                    id: currentFeedback.value.id,
                    reply: replyForm.value.reply,
                    status: 1
                }, {
                    params: {
                        role: '管理员'
                    }
                })
                if (res.code === '200') {
                    ElMessage.success('回复成功')
                    dialogVisible.value = false
                    loadFeedbackList()
                } else {
                    throw new Error(res.msg || '回复失败')
                }
            } catch (error) {
                console.error('提交回复失败:', error)
                ElMessage.error('回复失败：' + error.message)
            }
        }
    })
}

// 删除反馈
const handleDelete = async (row) => {
    try {
        const res = await request.delete(`/feedback/${row.id}`, {
            params: {
                role: '管理员'
            }
        })
        if (res.code === '200') {
            ElMessage.success('删除成功')
            loadFeedbackList()
        } else {
            throw new Error(res.msg || '删除失败')
        }
    } catch (error) {
        console.error('删除反馈失败:', error)
        ElMessage.error('删除失败：' + error.message)
    }
}

// 处理筛选变化
const handleFilterChange = () => {
    currentPage.value = 1
}

// 处理页码变化
const handleCurrentChange = (val) => {
    currentPage.value = val
}

// 处理每页条数变化
const handleSizeChange = (val) => {
    pageSize.value = val
    currentPage.value = 1
}

// 格式化日期
const formatDate = (date) => {
    if (!date) return ''
    const d = new Date(date)
    return d.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    })
}

onMounted(() => {
    loadFeedbackList()
})
</script>

<style scoped>
.feedback-manage {
    padding: 20px;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.right {
    display: flex;
    align-items: center;
    gap: 16px;
}

.refresh-btn {
    margin-left: 16px;
}

.feedback-content {
    padding: 12px;
    background-color: var(--el-fill-color-light);
    border-radius: 4px;
    margin-bottom: 10px;
    white-space: pre-wrap;
    word-break: break-all;
    line-height: 1.6;
}

.info-text {
    color: var(--el-text-color-regular);
    line-height: 32px;
}

.dialog-footer {
    margin-top: 20px;
}

.pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
}

:deep(.el-dialog__body) {
    padding-top: 10px;
}

:deep(.el-form-item__label) {
    font-weight: bold;
}
</style>
