<!--
*@
*@author Feiqi
*@date 2025/3/6 17:33
-->
<template>
    <div style="width: 50%">
        <div class="card" style="padding: 30px">
            <el-form :model="data.user" label-width="100px" style="padding-right: 50px" @submit.native.prevent>
                <div style="margin: 20px 0; text-align: center">
                    <el-upload :action="uploadUrl" :on-success="handleFileUpload" :show-file-list="false" class="avatar-uploader">
                        <img v-if="data.user.avatar" :src="assetUrl(data.user.avatar)" class="avatar"/>
                        <el-icon v-else class="avatar-uploader-icon">
                            <Plus/>
                        </el-icon>
                    </el-upload>
                </div>
                <el-form-item label="账号">
                    <el-input v-model="data.user.username" autocomplete="off" disabled/>
                </el-form-item>
                <el-form-item label="用户名">
                    <el-input v-model="data.user.name" autocomplete="off"/>
                </el-form-item>
                <el-form-item v-if="data.user.role !== '管理员'" label="电话" prop="phone">
                    <el-input v-model="data.user.phone" autocomplete="off" placeholder="请输入11位手机号码"/>
                </el-form-item>
                <el-form-item v-if="data.user.role !== '管理员'" label="邮箱" prop="email">
                    <el-input v-model="data.user.email" autocomplete="off" placeholder="选填"/>
                </el-form-item>
                <el-form-item v-if="data.user.role !== '管理员'" label="性别" prop="sex">
                    <el-select v-model="data.user.sex" placeholder="请选择性别" style="width: 100%">
                        <el-option label="男" value="男" />
                        <el-option label="女" value="女" />
                    </el-select>
                </el-form-item>
                <div style="text-align: center">
                    <el-button type="primary" @click="save">保存</el-button>
                </div>
            </el-form>
        </div>
    </div>
</template>

<script setup>
import {reactive, ref, onMounted} from "vue"
import request from "@/utils/request";
import {ElMessage} from "element-plus";
import { Plus } from "@element-plus/icons-vue";
import {apiUrl, assetUrl} from "@/utils/config";

/*文件上传的接口地址*/
const uploadUrl = apiUrl('/files/upload')

const data = reactive({
    user: JSON.parse(localStorage.getItem('currentUser') || '{}'),
    oldPhone: JSON.parse(localStorage.getItem('currentUser') || '{}').phone || ''
})

// 在组件挂载时打印信息
onMounted(() => {
    console.log('组件挂载，当前用户信息:', data.user)
    // 确保role字段是普通用户
    if (data.user.role === 'USER') {
        data.user.role = '普通用户'
        console.log('已修正用户角色为:', data.user.role)
    }
})

const handleFileUpload = (file) => {
    data.user.avatar = file.data
}

// 检查电话号码是否可用
const checkPhoneAvailable = async (phone, userId) => {
    try {
        const res = await request.get('/user/checkPhone', {
            params: {
                phone: phone,
                userId: userId
            }
        })
        console.log('电话检查结果:', res)
        return res.data
    } catch (error) {
        console.error('检查电话号码失败:', error)
        return false
    }
}

const emit = defineEmits(["updateUser"])
/*把当前修改的用户信息存储到后台数据库*/
const save = async () => {
    console.log('保存用户角色:', data.user.role) // 调试信息
    console.log('保存前完整用户数据:', data.user) // 完整调试信息

    // 确保用户角色设置正确
    if (data.user.role === 'USER') {
        data.user.role = '普通用户'
    }

    // 只有普通用户才需要验证电话号码等字段
    if (data.user.role !== '管理员') {
        // 验证手机号码
        if (!data.user.phone) {
            ElMessage.warning("手机号码不能为空！")
            return
        }
        if (!/^1[3-9]\d{9}$/.test(data.user.phone)) {
            ElMessage.warning("手机号码格式不正确！")
            return
        }

        // 如果电话号码变更了，检查是否可用
        if (data.user.phone !== data.oldPhone) {
            const isAvailable = await checkPhoneAvailable(data.user.phone, data.user.id)
            if (!isAvailable) {
                ElMessage.warning("该电话号码已被其他用户绑定！")
                return
            }
        }

        // 验证邮箱
        if (data.user.email && !/^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$/.test(data.user.email)) {
            ElMessage.warning("邮箱格式不正确！")
            return
        }
    }

    // 添加调试信息
    console.log('准备提交更新:', data.user)

    if (data.user.role === "管理员") {
        request.put('/admin/update', data.user).then(res => {
            console.log('管理员更新结果:', res)
            if (res.code === '200') {
                ElMessage.success('更新成功！')
                //把更新后的用户信息存储到缓存
                localStorage.setItem('currentUser', JSON.stringify(data.user))
                emit('updateUser')
            } else {
                ElMessage.error(res.msg || '更新失败')
            }
        }).catch(err => {
            console.error('管理员更新错误:', err)
            ElMessage.error(err.response?.data?.msg || '服务器错误')
        })
    } else {
        // 普通用户更新，确保字段完整
        const userToUpdate = { ...data.user }
        // 确保必要字段存在
        if (!userToUpdate.role) userToUpdate.role = '普通用户'

        console.log('最终提交数据:', userToUpdate)

        request.put('/user/update', userToUpdate).then(res => {
            console.log('普通用户更新结果:', res)
            if (res.code === '200') {
                ElMessage.success('更新成功！')
                //把更新后的用户信息存储到缓存
                data.oldPhone = data.user.phone // 更新成功后更新初始电话
                localStorage.setItem('currentUser', JSON.stringify(data.user))
                emit('updateUser')
            } else {
                ElMessage.error(res.msg || '更新失败')
            }
        }).catch(err => {
            console.error('普通用户更新错误:', err)
            // 尝试显示详细错误信息
            const errMsg = err.response?.data?.msg || (err.message ? err.message : '服务器错误')
            ElMessage.error(errMsg)
            // 更多错误信息
            console.log('错误详情:', {
                status: err.response?.status,
                headers: err.response?.headers,
                data: err.response?.data
            })
        })
    }
}
</script>

<style scoped>
.avatar-uploader .avatar {
    width: 120px;
    height: 120px;
    display: block;
}
</style>

<style>
.avatar-uploader .el-upload {
    border: 1px dashed var(--el-border-color);
    border-radius: 6px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    transition: var(--el-transition-duration-fast);
}

.avatar-uploader .el-upload:hover {
    border-color: var(--el-color-primary);
}

.el-icon.avatar-uploader-icon {
    font-size: 28px;
    color: #8c939d;
    width: 120px;
    height: 120px;
    text-align: center;
}
</style>
