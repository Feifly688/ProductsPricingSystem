<!--
*@
*@author Feiqi
*@date 2025/3/6 17:33
-->
<template>
    <div class="main-container">
        <!-- 背景元素 -->
        <div class="background-elements">
            <div v-for="i in 5" :key="i" class="price-tag"></div>
            <div v-for="i in 3" :key="i" class="cart-icon"></div>
            <div v-for="i in 4" :key="i" class="product-icon"></div>
            <div class="barcode"></div>
        </div>
        <!-- 顶部导航栏 -->
        <div class="header">
            <div class="logo-area">
                <div class="logo-container">
                    <el-icon class="logo-icon" size="28">
                        <ShoppingTrolley/>
                    </el-icon>
                    <div v-if="data.user.role==='普通用户'" class="logo-text">基于深度学习的商品计价系统</div>
                    <div v-else class="logo-text">商品计价后台管理系统</div>
                </div>
            </div>
            <div class="user-info">
                <el-dropdown trigger="click">
                    <div class="user-dropdown">
                        <img :src="assetUrl(data.user.avatar) || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'" alt="" class="user-avatar">
                        <span class="user-name">{{ data.user.name }}</span>
                        <el-icon class="dropdown-icon">
                            <arrow-down/>
                        </el-icon>
                    </div>
                    <template #dropdown>
                        <el-dropdown-menu>
                            <el-dropdown-item @click="router.push('/person')">
                                <el-icon>
                                    <User/>
                                </el-icon>
                                <span class="dropdown-item-text">个人中心</span>
                            </el-dropdown-item>
                            <el-dropdown-item @click="logout">
                                <el-icon>
                                    <SwitchButton/>
                                </el-icon>
                                <span class="dropdown-item-text">退出登录</span>
                            </el-dropdown-item>
                        </el-dropdown-menu>
                    </template>
                </el-dropdown>
            </div>
        </div>

        <div class="content-wrapper">
            <!-- 侧边栏 -->
            <div class="sidebar">
                <el-menu
                        :default-active="activeMenu"
                        :default-openeds="['1','2']"
                        class="sidebar-menu"
                        @select="handleSelect"
                >
                    <div class="menu-item-wrapper">
                        <el-menu-item index="/home">
                            <el-icon>
                                <HomeFilled/>
                            </el-icon>
                            <span>系统首页</span>
                        </el-menu-item>
                    </div>

                    <div v-if="data.user.role==='管理员'" class="menu-item-wrapper">
                        <el-menu-item index="/product">
                            <el-icon>
                                <Goods/>
                            </el-icon>
                            <span>商品列表</span>
                        </el-menu-item>
                    </div>

                    <div class="menu-item-wrapper">
                        <el-menu-item index="/predict">
                            <el-icon>
                                <Wallet/>
                            </el-icon>
                            <span>商品计价</span>
                        </el-menu-item>
                    </div>

                    <div v-if="data.user.role==='管理员'" class="menu-item-wrapper">
                        <el-menu-item index="/pricing-history">
                            <el-icon>
                                <Histogram/>
                            </el-icon>
                            <span>计价历史</span>
                        </el-menu-item>
                    </div>

                    <div v-if="data.user.role==='普通用户'" class="menu-item-wrapper">
                        <el-menu-item index="/user-pricing-history">
                            <el-icon>
                                <Histogram/>
                            </el-icon>
                            <span>我的计价历史</span>
                        </el-menu-item>
                    </div>

                    <div v-if="data.user.role==='管理员'" class="menu-item-wrapper">
                        <el-menu-item index="/compare">
                            <el-icon>
                                <Aim/>
                            </el-icon>
                            <span>模型对比</span>
                        </el-menu-item>
                    </div>

                    <div v-if="data.user.role==='管理员'" class="menu-item-wrapper">
                        <el-sub-menu index="2">
                            <template #title>
                                <el-icon>
                                    <Memo/>
                                </el-icon>
                                <span>用户管理</span>
                            </template>
                            <div class="submenu-item-wrapper">
                                <el-menu-item index="/admin">
                                    <el-icon>
                                        <Avatar/>
                                    </el-icon>
                                    <span>管理员信息</span>
                                </el-menu-item>
                            </div>
                            <div class="submenu-item-wrapper">
                                <el-menu-item index="/user">
                                    <el-icon>
                                        <User/>
                                    </el-icon>
                                    <span>普通用户信息</span>
                                </el-menu-item>
                            </div>
                        </el-sub-menu>
                    </div>
                    <div v-if="data.user.role==='普通用户'" class="menu-item-wrapper">
                        <el-menu-item index="/feedback">
                            <el-icon>
                                <ChatDotRound/>
                            </el-icon>
                            <span>反馈与建议</span>
                        </el-menu-item>
                    </div>

                    <div v-if="data.user.role==='管理员'" class="menu-item-wrapper">
                        <el-menu-item index="/feedback-manage">
                            <el-icon>
                                <ChatLineRound/>
                            </el-icon>
                            <span>反馈管理</span>
                        </el-menu-item>
                    </div>
                    <div class="menu-item-wrapper">
                        <el-menu-item index="/person">
                            <el-icon>
                                <User/>
                            </el-icon>
                            <span>个人资料</span>
                        </el-menu-item>
                    </div>

                    <div class="menu-item-wrapper">
                        <el-menu-item index="/password">
                            <el-icon>
                                <Lock/>
                            </el-icon>
                            <span>修改密码</span>
                        </el-menu-item>
                    </div>
                    <div class="menu-item-wrapper">
                        <el-menu-item @click="logout">
                            <el-icon>
                                <SwitchButton/>
                            </el-icon>
                            <span>退出系统</span>
                        </el-menu-item>
                    </div>
                </el-menu>
            </div>

            <!-- 主内容区 -->
            <div class="main-content">
                <!-- 标签页 -->
                <div class="tabs-container">
                    <el-tabs
                            v-model="activeTab"
                            class="custom-tabs"
                            closable
                            type="card"
                            @tab-remove="removeTab"
                            @tab-click="clickTab"
                    >
                        <el-tab-pane
                                v-for="item in tabs"
                                :key="item.path"
                                :label="item.title"
                                :name="item.path"
                        >
                            <template #label>
                                <div class="tab-label">
                                    <el-icon v-if="getTabIcon(item.path)" class="tab-icon">
                                        <component :is="getTabIcon(item.path)"/>
                                    </el-icon>
                                    <span>{{ item.title }}</span>
                                </div>
                            </template>
                        </el-tab-pane>
                    </el-tabs>
                </div>

                <!-- 页面内容 -->
                <div class="page-content">
                    <router-view v-if="useRouterView" v-slot="{ Component }" @updateUser="updateUser">
                        <transition mode="out-in" name="fade">
                            <keep-alive>
                                <component :is="Component"/>
                            </keep-alive>
                        </transition>
                    </router-view>
                    <component :is="currentComponent" v-else @updateUser="updateUser"/>
                </div>
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
import {computed, onMounted, reactive, ref, shallowRef} from "vue";
import router from "../router";
import {ElMessage, ElMessageBox} from "element-plus";
import {Aim, Avatar, ChatDotRound, ChatLineRound, Goods, Histogram, HomeFilled, Lock, Memo, ShoppingTrolley, SwitchButton, User, Wallet} from '@element-plus/icons-vue';
import {assetUrl} from "../utils/config";

// 定义路由标题映射
const routeTitles = {
    '/home': '系统首页',
    '/product': '商品列表',
    '/predict': '商品计价',
    '/pricing-history': '计价历史',
    '/user-pricing-history': '我的计价历史',
    '/compare': '模型对比',
    '/admin': '管理员信息',
    '/user': '普通用户信息',
    '/person': '个人资料',
    '/password': '修改密码',
    '/feedback': '反馈与建议',
    '/feedback-manage': '反馈管理'
};

// 定义路由图标映射
const routeIcons = {
    '/home': 'HomeFilled',
    '/product': 'Goods',
    '/predict': 'ShoppingCart',
    '/pricing-history': 'Histogram',
    '/user-pricing-history': 'Histogram',
    '/compare': 'Aim',
    '/admin': 'Avatar',
    '/user': 'User',
    '/person': 'User',
    '/password': 'Key',
    '/feedback': 'ChatDotRound',
    '/feedback-manage': 'ChatLineRound',
};

// 获取标签页图标
const getTabIcon = (path) => {
    return routeIcons[path] || null;
};

const data = reactive({
    user: JSON.parse(localStorage.getItem('currentUser') || '{}')
});

// 使用router-view（兼容模式）
const useRouterView = ref(true);

// 标签页数据
const tabs = ref([
    {
        title: '系统首页',
        path: '/home',
    }
]);

// 当前激活的标签
const activeTab = ref('/home');
// 当前激活的菜单项
const activeMenu = computed(() => activeTab.value);
// 当前需要显示的组件
const currentComponent = shallowRef(null);

// 初始化
onMounted(() => {
    // 初始化时添加当前路由到标签
    const currentPath = router.currentRoute.value.path;
    if (currentPath && currentPath !== '/') {
        if (routeTitles[currentPath]) {
            // 如果当前路径不是首页，则添加标签
            if (currentPath !== '/home') {
                tabs.value = [
                    {title: '系统首页', path: '/home'},
                    {title: routeTitles[currentPath], path: currentPath}
                ];
            }
            activeTab.value = currentPath;
        }
    }
});

// 处理菜单选择事件
const handleSelect = async (path) => {
    // 如果是点击退出系统，不做处理
    if (path === undefined) return;

    // 判断标签页是否已存在
    const exist = tabs.value.some(tab => tab.path === path);
    if (!exist) {
        // 添加新标签页
        tabs.value.push({
            title: routeTitles[path] || path,
            path: path
        });
    }

    // 激活对应标签
    activeTab.value = path;

    // 更新路由
    router.push(path);
};

// 点击标签切换
const clickTab = (tab) => {
    router.push(tab.props.name);
};

// 移除标签页
const removeTab = (targetPath) => {
    // 不允许关闭最后一个标签
    if (tabs.value.length === 1) {
        return ElMessage.warning('至少保留一个标签页');
    }

    // 找到要删除的标签索引
    const targetIndex = tabs.value.findIndex(tab => tab.path === targetPath);

    // 如果删除的是当前激活的标签，需要切换到其他标签
    if (activeTab.value === targetPath) {
        // 选择删除标签前一个标签或者后一个标签
        const nextTab = tabs.value[targetIndex - 1] || tabs.value[targetIndex + 1];
        activeTab.value = nextTab.path;
        router.push(nextTab.path);
    }

    // 删除标签
    tabs.value.splice(targetIndex, 1);
};

if (!data.user?.id) {
    ElMessage.error('请登录！')
    router.push('/login')
}

const updateUser = () => {
    data.user = JSON.parse(localStorage.getItem('currentUser') || '{}')
}

const logout = () => {
    ElMessageBox.confirm('确定要退出系统吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
    }).then(() => {
        ElMessage.success('退出成功！');
        localStorage.removeItem('currentUser');
        router.push('/login');
    }).catch(() => {
        ElMessage.info('取消退出');
    });
}


let beforeTime = 0, leaveTime = 0;

/*关闭浏览器时清除localstorage*/
window.onunload = () => {
    leaveTime = new Date().getTime() - beforeTime;
    if (leaveTime <= 5) {
        console.log("====关闭=====");
        localStorage.clear();
    } else {
        console.log("====刷新=====");
    }
};

window.onbeforeunload = () => {
    beforeTime = new Date().getTime();
};
</script>

<style scoped>
/* 全局容器 */
.main-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background-color: #f5f7fa;
    overflow: hidden;
    position: relative;
}

/* 背景元素 */
.background-elements {
    position: absolute;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 1;
    overflow: hidden;
}

.price-tag {
    position: absolute;
    width: 60px;
    height: 30px;
    border-radius: 20px;
    background: linear-gradient(135deg, rgba(75, 108, 183, 0.05), rgba(24, 40, 72, 0.1));
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
    opacity: 0.2;
}

.price-tag:nth-child(1) {
    top: 10%;
    left: 5%;
    animation: float 20s infinite ease-in-out;
}

.price-tag:nth-child(2) {
    top: 30%;
    right: 10%;
    animation: float 25s infinite ease-in-out reverse;
}

.price-tag:nth-child(3) {
    bottom: 15%;
    left: 15%;
    animation: float 22s infinite ease-in-out 1s;
}

.price-tag:nth-child(4) {
    bottom: 30%;
    right: 5%;
    animation: float 28s infinite ease-in-out 2s;
}

.price-tag:nth-child(5) {
    top: 50%;
    left: 80%;
    animation: float 26s infinite ease-in-out 3s;
}

.cart-icon {
    position: absolute;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: linear-gradient(135deg, rgba(255, 215, 0, 0.05), rgba(255, 215, 0, 0.1));
    opacity: 0.2;
}

.cart-icon:nth-child(6) {
    top: 20%;
    right: 20%;
    animation: float 26s infinite ease-in-out 1.5s;
}

.cart-icon:nth-child(7) {
    bottom: 10%;
    right: 30%;
    animation: float 24s infinite ease-in-out 3.5s;
}

.cart-icon:nth-child(8) {
    top: 60%;
    left: 10%;
    animation: float 30s infinite ease-in-out 2.5s;
}

.product-icon {
    position: absolute;
    width: 50px;
    height: 50px;
    border-radius: 8px;
    background: linear-gradient(135deg, rgba(240, 245, 255, 0.5), rgba(240, 245, 255, 0.2));
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
    opacity: 0.1;
}

.product-icon:nth-child(9) {
    top: 15%;
    left: 25%;
    animation: float 28s infinite ease-in-out 1s;
}

.product-icon:nth-child(10) {
    top: 40%;
    right: 25%;
    animation: float 25s infinite ease-in-out 2s;
}

.product-icon:nth-child(11) {
    bottom: 20%;
    left: 40%;
    animation: float 22s infinite ease-in-out 3s;
}

.product-icon:nth-child(12) {
    top: 70%;
    right: 15%;
    animation: float 26s infinite ease-in-out 4s;
}

.barcode {
    position: absolute;
    width: 100px;
    height: 40px;
    right: 10%;
    bottom: 5%;
    background: repeating-linear-gradient(
            to right,
            rgba(0, 0, 0, 0.03) 0px,
            rgba(0, 0, 0, 0.03) 2px,
            transparent 2px,
            transparent 4px
    );
    opacity: 0.2;
}

@keyframes float {
    0% {
        transform: translateY(0) translateX(0) rotate(0);
    }
    25% {
        transform: translateY(-15px) translateX(10px) rotate(2deg);
    }
    50% {
        transform: translateY(0) translateX(20px) rotate(0);
    }
    75% {
        transform: translateY(15px) translateX(10px) rotate(-2deg);
    }
    100% {
        transform: translateY(0) translateX(0) rotate(0);
    }
}

/* 顶部导航栏 */
.header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 60px;
    background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
    color: white;
    padding: 0 20px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    z-index: 10;
}

.logo-area {
    display: flex;
    align-items: center;
}

.logo-container {
    display: flex;
    align-items: center;
}

.logo-icon {
    color: #FFD700;
    margin-right: 10px;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.1);
    }
    100% {
        transform: scale(1);
    }
}

.logo-text {
    font-weight: bold;
    font-size: 22px;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
    background: linear-gradient(to right, #FFD700, #FFF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.user-info {
    display: flex;
    align-items: center;
}

.user-dropdown {
    display: flex;
    align-items: center;
    cursor: pointer;
    padding: 5px 10px;
    border-radius: 4px;
    transition: all 0.3s;
}

.user-dropdown:hover {
    background-color: rgba(255, 255, 255, 0.1);
}

.user-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: 2px solid rgba(255, 255, 255, 0.6);
    object-fit: cover;
}

.user-name {
    margin: 0 10px;
    font-weight: 500;
    color: white;
}

.dropdown-icon {
    color: rgba(255, 255, 255, 0.8);
}

.dropdown-item-text {
    margin-left: 8px;
}

/* 内容区 */
.content-wrapper {
    display: flex;
    flex: 1;
    overflow: hidden;
    position: relative;
    z-index: 2;
}

/* 侧边栏 */
.sidebar {
    width: 220px;
    background-color: #fff;
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.05);
    z-index: 5;
    overflow-y: auto;
    transition: width 0.3s;
}

.sidebar-menu {
    border-right: none;
    height: 100%;
}

.menu-item-wrapper {
    margin: 4px 0;
}

.submenu-item-wrapper {
    padding-left: 10px;
}

:deep(.el-menu-item) {
    height: 50px;
    line-height: 50px;
    border-radius: 6px;
    margin: 0 6px;
    transition: all 0.3s;
}

:deep(.el-menu-item.is-active) {
    background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
    color: white !important;
    box-shadow: 0 2px 8px rgba(75, 108, 183, 0.3);
}

:deep(.el-menu-item:hover) {
    background-color: #f0f5ff;
    color: #4b6cb7;
}

:deep(.el-sub-menu__title) {
    height: 50px;
    line-height: 50px;
    border-radius: 6px;
    margin: 0 6px;
}

:deep(.el-sub-menu__title:hover) {
    background-color: #f0f5ff;
}

:deep(.el-sub-menu.is-active .el-sub-menu__title) {
    color: #4b6cb7;
}

/* 主内容区 */
.main-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background-color: #f5f7fa;
    padding: 15px;
}

/* 标签页 */
.tabs-container {
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
    margin-bottom: 15px;
}

.custom-tabs {
    --el-tabs-header-height: 40px;
}

:deep(.el-tabs__header) {
    margin: 0;
    border-bottom: 1px solid #e6e6e6;
}

:deep(.el-tabs__nav) {
    border: none;
}

:deep(.el-tabs__item) {
    height: 40px;
    line-height: 40px;
    transition: all 0.3s;
    border-right: 1px solid #f0f0f0;
}

:deep(.el-tabs__item.is-active) {
    color: #4b6cb7;
    border-bottom: 2px solid #4b6cb7;
    font-weight: 500;
}

:deep(.el-tabs__item:hover) {
    color: #4b6cb7;
}

.tab-label {
    display: flex;
    align-items: center;
}

.tab-icon {
    margin-right: 5px;
    font-size: 16px;
}

/* 页面内容 */
.page-content {
    flex: 1;
    overflow-y: auto;
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
    padding: 20px;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}
</style>
