<!--
*@Product.vue
*@author Feiqi
*@date 2025/3/13 11:28
-->
<template>
    <div class="product-container">
        <!-- 搜索区域 -->
        <div class="search-section">
            <div class="section-title">
                <div class="title-left">
                    <el-icon><Search/></el-icon>
                    <span>商品搜索</span>
                </div>
            </div>
            <div class="search-form">
                <el-input
                        v-model="data.name"
                        clearable
                        placeholder="请输入商品名称查询"
                        prefix-icon="Search"
                        @keyup.enter.native="load"
                >
                </el-input>
                <el-button type="primary" @click="load">
                    <el-icon><Search/></el-icon>
                    <span>搜索</span>
                </el-button>
                <el-button type="info" @click="reset">
                    <el-icon><RefreshRight/></el-icon>
                    <span>重置</span>
                </el-button>
            </div>
        </div>

        <!-- 表格区域 -->
        <div class="table-section">
            <div class="section-title">
                <div class="title-left">
                    <el-icon><Goods/></el-icon>
                    <span>商品列表</span>
                </div>
                <div class="action-buttons">
                    <el-button size="small" type="primary" @click="handleAdd">
                        <el-icon><Plus/></el-icon>
                        <span>新增商品</span>
                    </el-button>
                </div>
            </div>
            <el-table
                    :data="data.tableData"
                    :header-cell-style="{ background: '#f5f7fa', color: '#606266' }"
                    border
                    class="product-table"
                    highlight-current-row
                    stripe
            >
                <!-- 添加序号列 -->
                <el-table-column align="center" label="序号" type="index" width="80">
                    <template #default="scope">
                        <div class="index-cell-container">
                            <span class="index-cell">{{ (data.pageNum - 1) * data.pageSize + scope.$index + 1 }}</span>
                        </div>
                    </template>
                </el-table-column>
                <el-table-column align="center" label="图片" width="120">
                    <template #default="scope">
                        <div class="image-container">
                            <el-image
                                    :preview-src-list="[scope.row.image]"
                                    :src="scope.row.image"
                                    class="product-image"
                                    fit="cover"
                                    preview-teleported
                            />
                        </div>
                    </template>
                </el-table-column>
                <el-table-column align="center" label="名称" min-width="180" prop="name">
                    <template #default="scope">
                        <div class="product-name">{{ scope.row.name }}</div>
                    </template>
                </el-table-column>
                <el-table-column align="center" label="价格" width="120">
                    <template #header>
                        <div class="custom-header">
                            <div class="sort-icons">
                                <div
                                  :class="['sort-icon-wrapper', data.sortColumn === 'price' && data.sortOrder === 'asc' ? 'active' : '']"
                                  @click="handleSort('price', 'asc')"
                                >
                                    <el-icon><CaretTop /></el-icon>
                                </div>
                                <div
                                  :class="['sort-icon-wrapper', data.sortColumn === 'price' && data.sortOrder === 'desc' ? 'active' : '']"
                                  @click="handleSort('price', 'desc')"
                                >
                                    <el-icon><CaretBottom /></el-icon>
                                </div>
                            </div>
                            价格
                        </div>
                    </template>
                    <template #default="scope">
                        <div class="price-container">
                            <span class="price-currency">¥</span>
                            <span class="price-value">{{ scope.row.price.toFixed(2) }}</span>
                        </div>
                    </template>
                </el-table-column>
                <el-table-column align="center" label="销售量" width="120">
                    <template #header>
                        <div class="custom-header">
                            <div class="sort-icons">
                                <div
                                  :class="['sort-icon-wrapper', data.sortColumn === 'sales' && data.sortOrder === 'asc' ? 'active' : '']"
                                  @click="handleSort('sales', 'asc')"
                                >
                                    <el-icon><CaretTop /></el-icon>
                                </div>
                                <div
                                  :class="['sort-icon-wrapper', data.sortColumn === 'sales' && data.sortOrder === 'desc' ? 'active' : '']"
                                  @click="handleSort('sales', 'desc')"
                                >
                                    <el-icon><CaretBottom /></el-icon>
                                </div>
                            </div>
                            销售量
                        </div>
                    </template>
                    <template #default="scope">
                        <div class="sales-container">
                            <el-tag :type="getSalesTagType(scope.row.sales)" effect="light" size="small">
                                {{ scope.row.sales || 0 }}
                            </el-tag>
                        </div>
                    </template>
                </el-table-column>
                <el-table-column align="center" label="操作" width="180">
                    <template #default="scope">
                        <div class="action-buttons">
                            <el-button size="small" type="primary" @click="handleEdit(scope.row)">
                                <el-icon><Edit/></el-icon>
                                <span>编辑</span>
                            </el-button>
                            <el-button disabled size="small" type="danger" @click="handleDelete(scope.row.id)">
                                <el-icon><Delete/></el-icon>
                                <span>删除</span>
                            </el-button>
                        </div>
                    </template>
                </el-table-column>
            </el-table>

            <!-- 分页区域 -->
            <div class="pagination-container">
                <el-pagination
                        v-model:current-page="data.pageNum"
                        v-model:page-size="data.pageSize"
                        :page-sizes="[10, 20, 50, 100]"
                        :total="data.total"
                        background
                        layout="total, sizes, prev, pager, next, jumper"
                        @current-change="load"
                        @size-change="handleSizeChange"
                />
            </div>
        </div>

        <!--添加/编辑弹窗-->
        <el-dialog
                v-model="data.formVisible"
                :title="data.form.id ? '编辑商品' : '添加商品'"
                class="product-dialog"
                destroy-on-close
                width="40%"
        >
            <el-form
                    :model="data.form"
                    label-width="80px"
                    @submit.native.prevent
            >
                <el-form-item label="商品图片" prop="image">
                    <el-upload
                            :action="uploadUrl"
                            :limit="1"
                            :on-success="handleImgSuccess"
                            accept="image/*"
                            class="product-upload"
                            list-type="picture-card"
                    >
                        <el-icon><Plus/></el-icon>
                        <template #file="{ file }">
                            <div class="upload-image-item">
                                <img :src="file.url" class="upload-image"/>
                            </div>
                        </template>
                    </el-upload>
                </el-form-item>
                <el-form-item label="商品名称">
                    <el-input v-model="data.form.name" autocomplete="off" placeholder="请输入商品名称" @keyup.enter.native="save"/>
                </el-form-item>
                <el-form-item label="商品价格">
                    <el-input-number v-model="data.form.price" :min="0" :precision="2" :step="0.01" placeholder="请输入商品价格"/>
                </el-form-item>
                <el-form-item v-if="data.form.id" label="销售量">
                    <el-input-number v-model="data.form.sales" :min="0" disabled placeholder="销售量"/>
                    <span class="form-hint">销售量为系统自动统计，不可手动修改</span>
                </el-form-item>
            </el-form>
            <template #footer>
                <div class="dialog-footer">
                    <el-button @click="data.formVisible = false">取 消</el-button>
                    <el-button type="primary" @click="save">保 存</el-button>
                </div>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import {reactive} from "vue";
import request from "../../utils/request";
import {ElMessage, ElMessageBox} from "element-plus";
import {
    CaretBottom,
    CaretTop,
    Delete,
    Edit,
    Goods,
    Plus,
    RefreshRight,
    Search
} from '@element-plus/icons-vue';

/*文件上传的接口地址*/
const uploadUrl = import.meta.env.VITE_BASE_URL + '/files/upload'

const data = reactive({
    tableData: [],
    total: 0,
    pageNum: 1,
    pageSize: 20,
    name: null,
    price: null,
    sales: 0,
    sortColumn: '',
    sortOrder: '',
    form: {},
    formVisible: false,
})

// 根据销售量返回不同的标签类型
const getSalesTagType = (sales) => {
    if (!sales) return 'error';
    if (sales >= 20) return 'success';
    if (sales >= 50) return 'warning';
    return 'info';
}

/*加载页面*/
const load = () => {
    console.log('加载数据，排序', data.sortColumn, data.sortOrder);
    request.get('/product/selectPage', {
        params: {
            pageNum: data.pageNum,
            pageSize: data.pageSize,
            name: data.name,
            price: data.price,
            sortColumn: data.sortColumn,
            sortOrder: data.sortOrder
        }
    }).then(res => {
        data.tableData = res.data.list
        data.total = res.data.total
    })
}

/*处理页码大小变化*/
const handleSizeChange = (size) => {
    data.pageSize = size;
    load();
}

/*处理排序*/
const handleSort = (column, order) => {
    console.log('点击排序：', column, order);
    if (data.sortColumn === column && data.sortOrder === order) {
        // 如果点击的是当前已激活的排序，则取消排序
        data.sortColumn = '';
        data.sortOrder = '';
    } else {
        data.sortColumn = column;
        data.sortOrder = order;
    }
    load(); // 重新加载数据
}

/*重置查询*/
const reset = () => {
    data.name = null;
    data.sortColumn = '';
    data.sortOrder = '';
    load();
}

/*新增*/
const handleAdd = () => {
    data.form = {}
    data.formVisible = true
}

/*新增保存*/
const add = () => {
    if (data.form.name != null && data.form.name !== "") {
        request.post('/product/add', data.form).then(res => {
            if (res.code === '200') {
                load()
                ElMessage.success('添加成功！')
                data.formVisible = false
            } else {
                ElMessage.error(res.msg)
            }
        })
    } else {
        ElMessage.warning("名称不能为空！")
    }
}
/*编辑*/
const handleEdit = (row) => {
    data.form = JSON.parse(JSON.stringify(row))
    data.formVisible = true
}
/*编辑保存*/
const update = () => {
    if (data.form.name != null && data.form.name !== "") {
        request.put('/product/update', data.form).then(res => {
            if (res.code === '200') {
                load()
                ElMessage.success('修改成功！')
                data.formVisible = false
            } else {
                ElMessage.error(res.msg)
            }
        })
    } else {
        ElMessage.warning("类别不能为空！")
    }
}
/*弹窗保存*/
const save = () => {
    /*有id就是更新，没有就是新增*/
    data.form.id ? update() : add()
}

/*删除*/
const handleDelete = (id) => {
    ElMessageBox.confirm('删除后数据无法恢复，您确定删除吗?', '删除确认', {type: 'warning'}).then(res => {
        request.delete('/product/delete/' + id).then(res => {
            if (res.code === '200') {
                load()
                ElMessage.success('删除成功！')
            } else {
                ElMessage.error(res.msg)
            }
        })
    }).catch(err => {
    })
}
/*处理文件上传的钩子*/
const handleImgSuccess = (res) => {
    data.form.image = res.data // res.data就是文件上传返回的文件路径，获取到路径后赋值表单的属性
}
load()
</script>

<style scoped>
.product-container {
    padding: 20px;
    background-color: #f5f7fa;
    min-height: calc(100vh - 60px);
}

.search-section, .table-section {
    background: linear-gradient(135deg, #ffffff 0%, #f9f9f9 100%);
    border-radius: 12px;
    padding: 25px;
    margin-bottom: 25px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.07);
    transition: box-shadow 0.3s;
}

.search-section:hover, .table-section:hover {
    box-shadow: 0 6px 25px rgba(0, 0, 0, 0.1);
}

.section-title {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    color: #303133;
    border-bottom: 2px solid #ebeef5;
    padding-bottom: 15px;
}

.title-left {
    display: flex;
    align-items: center;
}

.title-left .el-icon {
    margin-right: 10px;
    font-size: 22px;
    background: linear-gradient(135deg, #4b6cb7 0%, #182848 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    padding: 3px;
}

.search-form {
    display: flex;
    gap: 15px;
    align-items: center;
}

.search-form .el-input {
    max-width: 350px;
}

.search-form .el-button {
    border-radius: 8px;
    padding: 10px 20px;
    transition: all 0.3s;
}

.product-table {
    margin-top: 15px;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.image-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 5px;
}

.product-image {
    width: 80px;
    height: 80px;
    border-radius: 10px;
    object-fit: cover;
    transition: all 0.3s;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
}

.product-image:hover {
    transform: scale(1.08);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

.product-name {
    font-weight: 500;
    color: #303133;
    padding: 0 10px;
    white-space: normal;
    word-break: break-word;
    line-height: 1.5;
}

.custom-header {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    height: 100%;
    position: relative;
    padding: 0 8px;
}

.sort-icons {
    display: flex;
    flex-direction: column;
    margin-right: 8px;
    position: relative;
}

.sort-icon-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    cursor: pointer;
    transition: all 0.2s;
    border-radius: 4px;
}

.sort-icon-wrapper:hover {
    background-color: #ecf5ff;
}

.sort-icon-wrapper.active {
    background-color: #409EFF;
    color: white;
}

.price-container {
    display: flex;
    align-items: center;
    justify-content: center;
}

.price-currency {
    font-size: 12px;
    margin-right: 2px;
    color: #e6a23c;
}

.price-value {
    font-weight: 600;
    color: #e6a23c;
    font-size: 16px;
}

.sales-container {
    padding: 5px;
}

.index-cell-container {
    display: flex;
    justify-content: center;
    align-items: center;
}

.index-cell {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: linear-gradient(135deg, #e0e6ed 0%, #d7dde8 100%);
    font-size: 13px;
    font-weight: 600;
    color: #5e6c84;
}

.action-buttons {
    display: flex;
    gap: 10px;
    justify-content: center;
}

.action-buttons .el-button {
    border-radius: 6px;
    transition: all 0.3s;
}

.action-buttons .el-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.pagination-container {
    margin-top: 25px;
    display: flex;
    justify-content: flex-end;
    padding: 10px 0;
}

.product-dialog :deep(.el-upload--picture-card) {
    width: 140px;
    height: 140px;
    line-height: 140px;
    border-radius: 10px;
    border: 2px dashed #d9ecff;
    background-color: #f5f7fa;
}

.product-dialog :deep(.el-upload--picture-card:hover) {
    border-color: #409EFF;
    background-color: #ecf5ff;
}

.upload-image-item {
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
    border-radius: 8px;
}

.upload-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.form-hint {
    margin-left: 10px;
    color: #909399;
    font-size: 12px;
}

.dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    padding-top: 10px;
}

.product-dialog :deep(.el-dialog__header) {
    border-bottom: 1px solid #ebeef5;
    padding-bottom: 15px;
    margin-bottom: 15px;
}

.product-dialog :deep(.el-dialog__body) {
    padding: 20px 30px;
}
</style>
