<!--
*@
*@author Feiqi
*@date 2025/3/6 16:10
-->
<template>
    <div>
        <div class="card" style="margin-bottom: 5px;">
            <el-input v-model="data.username" placeholder="请输入账号查询" style="width: 200px; margin-right: 10px" @keyup.enter.native="load"></el-input>
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
                <el-table-column label="账号（唯一）" prop="username"></el-table-column>
                <el-table-column label="用户名" prop="name"></el-table-column>
                <el-table-column label="头像">
                    <template #default="scope">
                        <el-image :preview-src-list="[assetUrl(scope.row.avatar)]" :src="assetUrl(scope.row.avatar)" preview-teleported style="width: 40px; height: 40px; border-radius: 50%"></el-image>
                    </template>
                </el-table-column>
                <el-table-column label="角色" prop="role">
                    <template #default="scope">
                        <span v-if="scope.row.role === '管理员'">管理员</span>
                    </template>
                </el-table-column>
                <el-table-column align="center" label="操作" width="160">
                    <template #default="scope">
                        <!--<el-button type="primary" @click="handleEdit(scope.row)">编辑</el-button>-->
                        <el-button type="danger" @click="handleDelete(scope.row.id)" disabled>删除</el-button>
                    </template>
                </el-table-column>
            </el-table>
        </div>

        <div class="card">
            <el-pagination v-model:current-page="data.pageNum" v-model:page-size="data.pageSize" :total="data.total" layout="prev, pager, next,total" @current-change="load"/>
        </div>
    </div>
</template>

<script setup>
import request from "../../utils/request";
import {reactive} from "vue";
import {ElMessage, ElMessageBox} from "element-plus";
import {apiUrl, assetUrl} from "../../utils/config";

/*文件上传的接口地址*/
const uploadUrl = apiUrl('/files/upload')
const defaultAdminAvatar = apiUrl('/files/download/默认管理员头像.jpg')

const data = reactive({
    pageNum: 1,
    pageSize: 3,
    total: 0,
    formVisible: false,
    form: {},
    tableData: [],
    name: null
})

/*分页查询*/
const load = () => {
    request.get('/admin/selectPage', {
        params: {
            pageNum: data.pageNum,
            pageSize: data.pageSize,
            username: data.username
        }
    }).then(res => {
        data.tableData = res.data.list
        data.total = res.data.total
    })
}

/*新增*/
const handleAdd = () => {
    data.form = {
        avatar: defaultAdminAvatar
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
        request.post('/admin/add', data.form).then(res => {
            if (res.code === '200') {
                load()
                ElMessage.success('添加成功！')
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
        request.put('/admin/update', data.form).then(res => {
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
            request.delete('/admin/delete/' + id).then(res => {
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
    load()
}

/*处理文件上传的钩子*/
const handleImgSuccess = (res) => {
    data.form.avatar = res.data ? res.data : defaultAdminAvatar  // res.data就是文件上传返回的文件路径，获取到路径后赋值表单的属性
}

load()
</script>
