<!--
*@
*@author Feiqi
*@date 2025/4/15 16:21
-->
<template>
    <div>
        <!-- 反馈提交表单 -->
        <div class="card" style="padding: 20px; margin-bottom: 20px">
            <el-form :model="feedbackForm" label-width="100px">
                <el-form-item label="反馈内容">
                    <el-input
                            v-model="feedbackForm.content"
                            :rows="4"
                            placeholder="请输入您的反馈内容"
                            type="textarea"
                    />
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" @click="submitFeedback">提交反馈</el-button>
                </el-form-item>
            </el-form>
        </div>

        <!-- 历史反馈记录 -->
        <div class="card" style="padding: 20px">
            <h3>我的反馈记录</h3>
            <el-table :data="feedbackList" border style="width: 100%">
                <el-table-column label="反馈内容" prop="content"/>
                <el-table-column label="提交时间" prop="createTime" width="180"/>
                <el-table-column label="状态" prop="status" width="100">
                    <template #default="scope">
                        <el-tag :type="scope.row.status === 1 ? 'success' : 'info'">
                            {{ scope.row.status === 1 ? '已回复' : '未回复' }}
                        </el-tag>
                    </template>
                </el-table-column>
                <el-table-column label="管理员回复" prop="reply"/>
                <el-table-column label="回复时间" prop="replyTime" width="180"/>
            </el-table>
        </div>
    </div>
</template>

<script setup>
import {onMounted, ref} from 'vue'
import request from '../../utils/request'
import {ElMessage} from 'element-plus'

const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}')

const feedbackForm = ref({
    content: '',
    userId: currentUser.id,
    username: currentUser.name
})

const feedbackList = ref([])

// 获取当前用户的反馈记录
const loadFeedbackList = async () => {
    const res = await request.get('/feedback/user', {
        params: {userId: currentUser.id}
    })
    if (res.code === '200') {
        feedbackList.value = res.data
    }
}

// 提交反馈
const submitFeedback = async () => {
    if (!feedbackForm.value.content) {
        ElMessage.warning('请输入反馈内容')
        return
    }

    const res = await request.post('/feedback', feedbackForm.value)
    if (res.code === '200') {
        ElMessage.success('反馈提交成功')
        feedbackForm.value.content = ''
        loadFeedbackList()
    } else {
        ElMessage.error(res.msg)
    }
}

onMounted(() => {
    if (!currentUser.id) {
        ElMessage.error('请先登录')
        return
    }
    loadFeedbackList()
})
</script>

<style scoped>
.card {
    background: #fff;
    border-radius: 4px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, .1);
}
</style>
