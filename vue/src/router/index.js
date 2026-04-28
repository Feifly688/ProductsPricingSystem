import { createRouter, createWebHistory } from 'vue-router';
import { ElMessage } from 'element-plus';

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            component: () => import('../views/Manager.vue'),
            redirect: '/home',
            children: [
                { path: 'person', component: () => import('../views/manager/Person.vue') },
                { path: 'password', component: () => import('../views/manager/Password.vue') },
                { path: 'home', component: () => import('../views/manager/Home.vue') },
                { path: 'admin', component: () => import('../views/manager/Admin.vue') },
                { path: 'user', component: () => import('../views/manager/User.vue') },
                { path: 'product', component: () => import('../views/manager/Product.vue') },
                { path: 'train', component: () => import('../views/manager/Train.vue') },
                { path: 'predict', component: () => import('../views/manager/Predict.vue') },
                { path: 'compare', component: () => import('../views/manager/Compare.vue') },
                { path: 'pricing-history', component: () => import('../views/manager/PricingHistory.vue') },
                { path: 'feedback', component: () => import('../views/manager/FeedBack.vue') },
                { path: 'feedback-manage', component: () => import('../views/manager/FeedBackManager.vue') },
            ]
        },
        { path: '/login', component: () => import('../views/Login.vue') },
        { path: '/register', component: () => import('../views/Register.vue') },
    ]
});

router.beforeEach((to, from, next) => {
    if (to.path === '/login' || to.path === '/register') {
        return next();
    }

    const userText = localStorage.getItem('currentUser');
    if (!userText) {
        return next('/login');
    }

    let user;
    try {
        user = JSON.parse(userText);
    } catch (error) {
        localStorage.removeItem('currentUser');
        sessionStorage.removeItem('user');
        return next('/login');
    }

    const adminOnlyPaths = ['/compare', '/product', '/train', '/admin', '/user', '/feedback-manage', '/pricing-history'];
    if (user.role !== '管理员' && adminOnlyPaths.includes(to.path)) {
        ElMessage.warning('您不是管理员，没有权限访问！');
        return next('/');
    }

    if (user.role !== '普通用户' && to.path === '/feedback') {
        ElMessage.warning('请管理员使用反馈管理查看');
        return next('/');
    }

    next();
});

export default router;
