import {createRouter, createWebHistory} from 'vue-router'
import {ElMessage} from "element-plus";

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            component: () => import('../views/Manager.vue'),
            redirect: '/home',
            children: [
                {path: 'person', component: () => import('../views/manager/Person.vue')},
                {path: 'password', component: () => import('../views/manager/Password.vue')},
                {path: 'home', component: () => import('../views/manager/Home.vue')},
                {path: 'admin', component: () => import('../views/manager/Admin.vue')},
                {path: 'user', component: () => import('../views/manager/User.vue')},
                {path: 'product', component: () => import('../views/manager/Product.vue')},
                {path: 'train', component: () => import('../views/manager/Train.vue')},
                {path: 'predict', component: () => import('../views/manager/Predict.vue')},
                {path: 'compare', component: () => import('../views/manager/Compare.vue')},
                {path: 'pricing-history', component: () => import('../views/manager/PricingHistory.vue')},
                {path: 'feedback', component: () => import('../views/manager/FeedBack.vue')},
                {path: 'feedback-manage', component: () => import('../views/manager/FeedBackManager.vue')},
            ]
        },
        {path: '/login', component: () => import('../views/Login.vue')},
        {path: '/register', component: () => import('../views/Register.vue')},
    ]
})
/*路由守卫*/
router.beforeEach((to, from, next) => {
    if (to.path === '/login') {
        next();
    }
    if (to.path === '/register') {
        next();
    }
    const user = localStorage.getItem("currentUser");
    if (!user && to.path !== '/login') {
        return next('/login');
    }
    if (JSON.parse(user).role !== '管理员' && (to.path === '/compare' || to.path === '/product' || to.path === '/train' || to.path === '/admin' || to.path === '/user' || to.path === '/feedback-manager')) { //若不是管理员，则不能访问
        ElMessage.warning("您不是管理员，没有权限访问！")
        return next('/')
    }
    if (JSON.parse(user).role !== '普通用户' && (to.path === '/feedback')) {
        ElMessage.warning('请管理员使用反馈管理查看')
        return next('/')
    }
    next();
})
export default router
