<template>
    <div class="cyber-container" @mousemove="handleMouseMove">
        <div class="bg-layer">
            <canvas ref="networkCanvas" class="network-canvas"></canvas>
            <div class="radar-circle"></div>
            <div class="code-rain">
                <span v-for="n in 10" :key="n" :style="{left: Math.random()*90 + '%', animationDelay: Math.random()*5 + 's'}">
                    {{ Math.random() > 0.5 ? '10101' : '01010' }}
                </span>
            </div>
        </div>

        <div class="login-wrapper" :style="cardStyle">
            <div class="hologram-border"></div>

            <div class="register-box">
                <div class="hud-corner top-left"></div>
                <div class="hud-corner top-right"></div>
                <div class="hud-corner bottom-left"></div>
                <div class="hud-corner bottom-right"></div>
                <div class="scan-line"></div>

                <div class="header">
                    <div class="logo-area">
                        <div class="hex-bg">
                            <el-icon class="logo-icon" size="32"><ShoppingBag /></el-icon>
                        </div>
                    </div>
                    <h2 class="title">
                        注册 <span class="highlight">权限终端</span>
                    </h2>
                    <p class="subtitle">启动新用户协议</p>
                </div>

                <el-form ref="formRef" :model="data.form" :rules="data.rules" class="cyber-form" size="large">
                    <el-form-item prop="username">
                        <div class="input-group">
                            <el-input v-model="data.form.username" :prefix-icon="User" placeholder="访问 ID // 账号" class="cyber-input"/>
                            <div class="input-focus-border"></div>
                        </div>
                    </el-form-item>
                    <el-form-item prop="name">
                        <div class="input-group">
                            <el-input v-model="data.form.name" :prefix-icon="Edit" placeholder="用户名称 // 昵称" class="cyber-input"/>
                            <div class="input-focus-border"></div>
                        </div>
                    </el-form-item>
                    <el-form-item prop="password">
                        <div class="input-group">
                            <el-input v-model="data.form.password" :prefix-icon="Lock" placeholder="访问密码 // 密码" show-password class="cyber-input"/>
                            <div class="input-focus-border"></div>
                        </div>
                    </el-form-item>
                    <el-form-item prop="confirmPassword">
                        <div class="input-group">
                            <el-input v-model="data.form.confirmPassword" :prefix-icon="Check" placeholder="确认密码 // 校验" show-password class="cyber-input"/>
                            <div class="input-focus-border"></div>
                        </div>
                    </el-form-item>

                    <el-form-item>
                        <el-button class="cyber-btn" @click="register">
                            <span class="btn-content">
                                <span class="btn-text">注册接入</span>
                                <span class="btn-decoration"></span>
                            </span>
                        </el-button>
                    </el-form-item>
                </el-form>

                <div class="status-bar">
                    <a href="/login" class="reg-link">返回登录端口</a>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { onMounted, onUnmounted, reactive, ref, computed } from "vue";
import { Lock, User, ShoppingBag, Edit, Check } from "@element-plus/icons-vue";
import request from "../utils/request";
import { ElMessage } from "element-plus";
import router from "../router";

const formRef = ref();
const networkCanvas = ref(null);
const mouseX = ref(0);
const mouseY = ref(0);

const data = reactive({
    form: {
        username: '',
        name: '',
        password: '',
        confirmPassword: '',
        role: '普通用户'
    },
    rules: {
        username: [{ required: true, message: '访问ID不能为空', trigger: 'blur' }],
        name: [{ required: true, message: '用户名称不能为空', trigger: 'blur' }],
        password: [{ required: true, message: '访问密码不能为空', trigger: 'blur' }],
        confirmPassword: [
            { required: true, message: '请再次输入密码', trigger: 'blur' },
            {
                validator: (rule, value, callback) => {
                    if (value !== data.form.password) {
                        callback(new Error('两次密码输入不一致'));
                    } else {
                        callback();
                    }
                },
                trigger: 'blur'
            }
        ]
    }
});

const handleMouseMove = (e) => {
    const x = (e.clientX / window.innerWidth) * 2 - 1;
    const y = (e.clientY / window.innerHeight) * 2 - 1;
    mouseX.value = x;
    mouseY.value = y;
};
const cardStyle = computed(() => {
    const rotateX = -mouseY.value * 5;
    const rotateY = mouseX.value * 5;
    return {
        transform: `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`
    };
});

// ... (initNetwork, onMounted, onUnmounted 逻辑保持不变) ...

const initNetwork = () => { /* ... 动画逻辑 ... */ };

onMounted(() => { initNetwork(); });

onUnmounted(() => { /* ... 清理逻辑 ... */ });

const register = () => {
    formRef.value.validate((valid) => {
        if (valid) {
            const { confirmPassword, ...registerData } = data.form;
            request.post('/register', registerData).then(res => {
                if (res.code === '200') {
                    ElMessage.success("注册成功，正在跳转...");
                    router.push('/login');
                } else {
                    ElMessage.error(res.msg || "注册失败！");
                }
            });
        }
    });
};
</script>

<style scoped>
/* 样式与通用 SCSS/CSS 保持一致，但注意中文标题无需大写 */
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&display=swap');

/* ... (样式代码与上一轮保持一致) ... */

/* 头部样式调整，以适应中文 */
.title { font-size: 28px; letter-spacing: 2px; margin: 0; font-weight: 700; } /* 移除 text-transform: uppercase; */
.subtitle { font-size: 14px; color: #6a85a0; margin-top: 5px; letter-spacing: 1px; }

/* 链接调整 */
.reg-link { color: #6a85a0; text-decoration: none; transition: color 0.3s; } /* 移除 text-transform: uppercase; */
.reg-link:hover { color: #00f3ff; }

</style>
<style scoped>
/* 引入外部字体 */
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&display=swap');

/* 全局容器 (与 Login.vue 保持一致) */
.cyber-container {
    width: 100vw;
    height: 100vh;
    background-color: #050505;
    position: relative;
    overflow: hidden;
    font-family: 'Rajdhani', sans-serif;
    color: #fff;
    display: flex;
    justify-content: center;
    align-items: center;
}

/* === 背景层 (与 Login.vue 保持一致) === */
.bg-layer {
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%; z-index: 0;
    background: radial-gradient(circle at center, #111b29 0%, #000 100%);
}
.network-canvas { position: absolute; top: 0; left: 0; z-index: 1; opacity: 0.6; }
.radar-circle {
    position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
    width: 800px; height: 800px; border: 1px dashed rgba(0, 243, 255, 0.1); border-radius: 50%;
    animation: rotate 60s linear infinite; z-index: 0;
}
.radar-circle::before {
    content: ''; position: absolute; top: -1px; left: 50%; width: 10px; height: 10px;
    background: #00f3ff; box-shadow: 0 0 20px #00f3ff; border-radius: 50%;
}
.code-rain span {
    position: absolute; top: -50px; color: rgba(0, 243, 255, 0.2); font-size: 14px;
    writing-mode: vertical-rl; animation: rain 4s linear infinite; user-select: none;
}

/* === 登录视差容器 (与 Login.vue 保持一致) === */
.login-wrapper {
    position: relative; z-index: 10; transition: transform 0.1s ease-out;
}

/* 注册框主体 */
.register-box {
    width: 400px;
    padding: 40px;
    background: rgba(10, 15, 30, 0.65);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(0, 243, 255, 0.2);
    box-shadow: 0 0 50px rgba(0, 0, 0, 0.8), inset 0 0 30px rgba(0, 243, 255, 0.05);
    position: relative;
}

/* 全息边框光效 */
.hologram-border {
    position: absolute; top: -2px; left: -2px; right: -2px; bottom: -2px; z-index: -1;
    background: linear-gradient(45deg, transparent 40%, #00f3ff 50%, transparent 60%);
    background-size: 200% 200%; animation: borderShine 4s linear infinite; opacity: 0.5;
}

/* HUD 四角瞄准器 */
.hud-corner {
    position: absolute; width: 15px; height: 15px; border: 2px solid #00f3ff; transition: all 0.3s ease;
}
.top-left { top: -1px; left: -1px; border-right: 0; border-bottom: 0; }
.top-right { top: -1px; right: -1px; border-left: 0; border-bottom: 0; }
.bottom-left { bottom: -1px; left: -1px; border-right: 0; border-top: 0; }
.bottom-right { bottom: -1px; right: -1px; border-left: 0; border-top: 0; }
.register-box:hover .top-left { transform: translate(-5px, -5px); }
.register-box:hover .top-right { transform: translate(5px, -5px); }
.register-box:hover .bottom-left { transform: translate(-5px, 5px); }
.register-box:hover .bottom-right { transform: translate(5px, 5px); }

/* 顶部扫描线 */
.scan-line {
    position: absolute; top: 0; left: 0; width: 100%; height: 2px;
    background: #00f3ff; box-shadow: 0 0 10px #00f3ff; animation: scan 3s ease-in-out infinite; opacity: 0.5;
}

.logo-area { display: flex; justify-content: center; margin-bottom: 15px; }
.hex-bg {
    width: 60px; height: 60px; background: rgba(0, 243, 255, 0.1);
    clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
    display: flex; justify-content: center; align-items: center; border: 1px solid rgba(0, 243, 255, 0.3);
}
.logo-icon { color: #00f3ff; filter: drop-shadow(0 0 5px #00f3ff); }
.title { font-size: 28px; letter-spacing: 2px; margin: 0; font-weight: 700; } /* 移除 text-transform: uppercase; */

.highlight { color: #00f3ff; }
/* 输入框交互增强 */
.input-group { position: relative; width: 100%; }
.input-focus-border {
    position: absolute; bottom: 0; left: 50%; width: 0; height: 2px;
    background: #00f3ff; transition: all 0.4s ease; box-shadow: 0 0 10px #00f3ff; z-index: 2;
}
:deep(.cyber-input .el-input__wrapper) { /* 深度选择器覆盖 Element 样式 */
    background-color: rgba(0, 0, 0, 0.3) !important; box-shadow: none !important;
    border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 0; padding-left: 15px;
}
:deep(.cyber-input .el-input__wrapper.is-focus) {
    border-color: rgba(0, 243, 255, 0.5); background-color: rgba(0, 243, 255, 0.05) !important;
}
:deep(.cyber-input .el-input__wrapper.is-focus) + .input-focus-border { /* 聚焦光条展开 */
    width: 100%; left: 0;
}
:deep(.el-input__inner) { color: #fff !important; font-family: 'Rajdhani', sans-serif; letter-spacing: 1px; height: 40px; }
:deep(.el-input__prefix-inner) { color: #00f3ff; }

/* 按钮样式 (能量填充) */
.cyber-btn {
    width: 100%; height: 50px; background: transparent !important; border: 1px solid #00f3ff !important;
    color: #00f3ff !important; position: relative; overflow: hidden; transition: all 0.3s; border-radius: 0;
}
.cyber-btn::before { content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: #00f3ff; transition: left 0.4s ease; z-index: 0; }
.cyber-btn:hover::before { left: 0; }
.cyber-btn:hover { color: #000 !important; box-shadow: 0 0 20px rgba(0, 243, 255, 0.4); }
.btn-content { position: relative; z-index: 1; display: flex; justify-content: center; width: 100%; font-weight: 700; letter-spacing: 2px; }


/* 底部状态栏 */
.status-bar {
    display: flex; justify-content: center; align-items: center; margin-top: 25px;
    padding-top: 15px; border-top: 1px solid rgba(255, 255, 255, 0.1); font-size: 12px;
    color: #4a5d73;
}

/* 动画定义 (与 Login.vue 保持一致) */
@keyframes rotate { 100% { transform: translate(-50%, -50%) rotate(360deg); } }
@keyframes rain { 100% { top: 100%; opacity: 0; } }
@keyframes borderShine { 0% { background-position: 0% 50%; } 100% { background-position: 100% 50%; } }
@keyframes scan { 0% { top: 0%; opacity: 0; } 50% { opacity: 1; } 100% { top: 100%; opacity: 0; } }
</style>
