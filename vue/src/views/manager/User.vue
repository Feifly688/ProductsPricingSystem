<!--
*@
*@author Feiqi
*@date 2025/3/6 19:15
-->
<template>
    <div>
        <div class="card" style="margin-bottom: 5px;">
            <el-input v-model="data.username" placeholder="请输入账号查询" style="width: 200px; margin-right: 10px" @keyup.enter.native="load"></el-input>
            <el-input v-model="data.phone" placeholder="请输入电话查询" style="width: 200px; margin-right: 10px" @keyup.enter.native="load"></el-input>
            <el-button type="primary" @click="load">
                <el-icon>
                    <Search/>
                </el-icon>
            </el-button>
            <el-button style="margin: 0 10px" type="info" @click="reset">重置</el-button>
        </div>

        <div class="card" style="margin-bottom: 5px">
            <div style="margin-bottom: 10px">
                <!--<el-button type="primary" @click="handleAdd">新增</el-button>-->
            </div>
            <el-table :data="data.tableData" stripe>
                <!-- 添加序号列 -->
                <el-table-column label="序号" type="index" width="80">
                    <template #default="scope">
                        {{ (data.pageNum - 1) * data.pageSize + scope.$index + 1 }}
                    </template>
                </el-table-column>
                <el-table-column label="账号" prop="username"></el-table-column>
                <el-table-column label="用户名" prop="name"></el-table-column>
                <el-table-column label="电话" prop="phone"></el-table-column>
                <el-table-column label="邮箱" prop="email">
                    <template #default="scope">
                        <span>{{ scope.row.email || '未绑定' }}</span>
                    </template>
                </el-table-column>
                <el-table-column label="性别" prop="sex">
                    <template #default="scope">
                        <span>{{ scope.row.sex || '未知' }}</span>
                    </template>
                </el-table-column>
                <el-table-column label="头像">
                    <template #default="scope">
                        <el-image :preview-src-list="[assetUrl(scope.row.avatar)]" :src="assetUrl(scope.row.avatar)" preview-teleported style="width: 40px; height: 40px; border-radius: 50%"></el-image>
                    </template>
                </el-table-column>
                <el-table-column label="角色" prop="role">
                    <template #default="scope">
                        <span v-if="scope.row.role === '普通用户'">普通用户</span>
                    </template>
                </el-table-column>
                <el-table-column align="center" label="操作" width="160">
                    <template #default="scope">
                        <!--<el-button type="primary" @click="handleEdit(scope.row)">编辑</el-button>-->
                        <el-button type="danger" @click="handleDelete(scope.row.id)">删除</el-button>
                    </template>
                </el-table-column>
            </el-table>
        </div>

        <div class="card">
            <el-pagination v-model:current-page="data.pageNum" v-model:page-size="data.pageSize" :total="data.total" layout="prev, pager, next, total" @current-change="load"/>
        </div>
        <!--添加弹窗-->
        <el-dialog v-model="data.formVisible" :close-on-click-modal="false" destroy-on-close title="用户信息" width="40%">
            <el-form :model="data.form" label-width="100px" style="padding-right: 50px" @submit.native.prevent>
                <el-form-item label="头像" prop="avatar">
                    <el-upload :action="uploadUrl" :on-success="handleImgSuccess" list-type="picture">
                        <el-button type="primary">上传图片</el-button>
                    </el-upload>
                </el-form-item>
                <el-form-item label="用户名" prop="username">
                    <el-input v-model="data.form.username" autocomplete="off"/>
                </el-form-item>
                <el-form-item label="名字" prop="name">
                    <el-input v-model="data.form.name" autocomplete="off"/>
                </el-form-item>
                <el-form-item label="电话" prop="phone">
                    <el-input v-model="data.form.phone" autocomplete="off"/>
                </el-form-item>
                <el-form-item label="邮箱" prop="email">
                    <el-input v-model="data.form.email" autocomplete="off" placeholder="选填"/>
                </el-form-item>
                <el-form-item label="性别" prop="sex">
                    <el-select v-model="data.form.sex" placeholder="请选择性别" style="width: 100%">
                        <el-option label="男" value="男" />
                        <el-option label="女" value="女" />
                    </el-select>
                </el-form-item>
            </el-form>
            <template #footer>
      <span class="dialog-footer">
        <el-button @click="data.formVisible = false">取 消</el-button>
        <el-button type="primary" @click="save">保 存</el-button>
      </span>
            </template>
        </el-dialog>

    </div>
</template>

<script setup>
import request from "../../utils/request";
import {reactive} from "vue";
import {ElMessage, ElMessageBox} from "element-plus";
import {apiUrl, assetUrl} from "../../utils/config";

/*文件上传的接口地址*/
const uploadUrl = apiUrl('/files/upload')
const defaultUserAvatar = apiUrl('/files/download/默认头像.jpg')

const data = reactive({
    pageNum: 1,
    pageSize: 6,
    total: 0,
    formVisible: false,
    form: {},
    tableData: [],
    username: null,
    phone: null
})

/*分页查询*/
const load = (newPage) => {
    request.get('/user/selectPage', {
        params: {
            pageNum: data.pageNum,
            pageSize: data.pageSize,
            username: data.username,
            phone: data.phone
        }
    }).then(res => {
        data.tableData = res.data.list
        data.total = res.data.total
    })
}

/*新增*/
const handleAdd = () => {
    data.form = {
        avatar: defaultUserAvatar
    }
    data.formVisible = true
}

/*编辑*/
const handleEdit = (row) => {
    data.form = JSON.parse(JSON.stringify(row))
    data.formVisible = true
}

/*新增保存*/
const add = () => {
    if (data.form.username != null && data.form.username !== "") {
        // 验证电话号码
        if (!data.form.phone) {
            ElMessage.warning("电话号码不能为空！")
            return
        }
        if (!/^1[3-9]\d{9}$/.test(data.form.phone)) {
            ElMessage.warning("电话号码格式不正确！")
            return
        }

        // 验证邮箱
        if (data.form.email && !/^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$/.test(data.form.email)) {
            ElMessage.warning("邮箱格式不正确！")
            return
        }

        request.post('/user/add', data.form).then(res => {
            if (res.code === '200') {
                load()
                ElMessage.success('操作成功')
                data.formVisible = false
            } else {
                ElMessage.error(res.msg)
            }
        })
    } else {
        ElMessage.warning("用户名不能为空！")
    }
}

/*编辑保存*/
const update = () => {
    if (data.form.username != null && data.form.username !== "") {
        // 验证电话号码
        if (!data.form.phone) {
            ElMessage.warning("电话号码不能为空！")
            return
        }
        if (!/^1[3-9]\d{9}$/.test(data.form.phone)) {
            ElMessage.warning("电话号码格式不正确！")
            return
        }

        // 验证邮箱
        if (data.form.email && !/^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$/.test(data.form.email)) {
            ElMessage.warning("邮箱格式不正确！")
            return
        }

        request.put('/user/update', data.form).then(res => {
            if (res.code === '200') {
                load()
                ElMessage.success('修改成功！')
                data.formVisible = false
            } else {
                ElMessage.error(res.msg)
            }
        })
    } else {
        ElMessage.warning("用户名不能为空！")
    }
}

/*弹窗保存*/
const save = () => {
    // data.form有id就是更新，没有就是新增
    data.form.id ? update() : add()
}

/*删除*/
const handleDelete = (id) => {
    ElMessageBox.confirm('删除后数据无法恢复，您确定删除吗?', '删除确认', {type: 'warning'}).then(res => {
        const curId = JSON.parse(localStorage.getItem('currentUser')).id
        if (curId !== id) {
            request.delete('/user/delete/' + id).then(res => {
                        if (res.code === '200') {
                            load()
                            ElMessage.success('删除成功！')
                        } else {
                            ElMessage.error(res.msg)
                        }
                    }
            )
        } else {
            ElMessage.error("不能删除当前正在登录的用户！")
        }
    }).catch(err => {
    })
}

/*重置*/
const reset = () => {
    data.username = null
    data.phone = null
    load()
}

/*处理文件上传的钩子*/
const handleImgSuccess = (res) => {
    data.form.avatar = res.data // res.data就是文件上传返回的文件路径，获取到路径后赋值表单的属性
}

load()
</script>

