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

        <div class="login-wrapper" ref="loginCardRef" :style="cardStyle">
            <div class="hologram-border"></div>

            <div class="login-box">
                <div class="hud-corner top-left"></div>
                <div class="hud-corner top-right"></div>
                <div class="hud-corner bottom-left"></div>
                <div class="hud-corner bottom-right"></div>

                <div class="scan-line"></div>

                <div class="header">
                    <div class="logo-area">
                        <div class="hex-bg">
                            <el-icon class="logo-icon" size="32"><ShoppingTrolley /></el-icon>
                        </div>
                    </div>
                    <h2 class="title">
                        VISION <span class="highlight">AI</span> SYSTEM
                    </h2>
                    <p class="subtitle">深度学习多目标检测商品计价终端</p>
                </div>

                <el-form ref="formRef" :model="data.form" :rules="data.rules" class="cyber-form" size="large">
                    <el-form-item prop="username">
                        <div class="input-group">
                            <el-input
                                    v-model="data.form.username"
                                    :prefix-icon="User"
                                    placeholder="ACCESS ID // 账号"
                                    class="cyber-input"
                            />
                            <div class="input-focus-border"></div>
                        </div>
                    </el-form-item>

                    <el-form-item prop="password">
                        <div class="input-group">
                            <el-input
                                    v-model="data.form.password"
                                    :prefix-icon="Lock"
                                    placeholder="PASSCODE // 密码"
                                    show-password
                                    class="cyber-input"
                            />
                            <div class="input-focus-border"></div>
                        </div>
                    </el-form-item>

                    <el-form-item prop="role">
                        <div class="input-group">
                            <el-select
                                    v-model="data.form.role"
                                    style="width: 100%"
                                    popper-class="cyber-select-dropdown"
                                    class="cyber-select"
                            >
                                <el-option label="管理员 [ROOT]" value="管理员"></el-option>
                                <el-option label="操作员 [USER]" value="普通用户"></el-option>
                            </el-select>
                        </div>
                    </el-form-item>

                    <el-form-item prop="captcha">
                        <div class="captcha-row">
                            <el-input
                                    v-model="data.form.captcha"
                                    :prefix-icon="Key"
                                    placeholder="VERIFICATION"
                                    class="cyber-input small"
                                    @keyup.enter="login"
                            />
                            <div class="captcha-box" @click="refreshCaptcha" title="点击刷新">
                                <canvas ref="captchaCanvas" width="100" height="42"></canvas>
                                <div class="glitch-overlay"></div>
                            </div>
                        </div>
                    </el-form-item>

                    <el-form-item>
                        <el-button
                                class="cyber-btn"
                                :loading="isLoading"
                                @click="login"
                        >
                            <span class="btn-content">
                                <span class="btn-text">{{ isLoading ? '连接中......' : '登录' }}</span>
                                <span class="btn-decoration"></span>
                            </span>
                        </el-button>
                    </el-form-item>
                </el-form>

                <div class="status-bar">
                    <div class="status-dot"></div>
                    <span>SYSTEM ONLINE</span>
                    <a href="/register" class="reg-link">注册新用户</a>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { onMounted, onUnmounted, reactive, ref, computed } from "vue";
import { Key, Lock, ShoppingTrolley, User } from "@element-plus/icons-vue";
import request from "../utils/request";
import { ElMessage } from "element-plus";
import router from "../router";

// Refs
const formRef = ref();
const captchaCanvas = ref(null);
const networkCanvas = ref(null);
const loginCardRef = ref(null);
const isLoading = ref(false);

// Mouse Position for Parallax
const mouseX = ref(0);
const mouseY = ref(0);

// Data
const data = reactive({
    form: {
        username: '',
        password: '',
        role: '普通用户',
        captcha: ''
    },
    captchaCode: '',
    rules: {
        username: [{ required: true, message: 'ID REQUIRED', trigger: 'blur' }],
        password: [{ required: true, message: 'PASSCODE REQUIRED', trigger: 'blur' }],
        captcha: [
            { required: true, message: 'MISSING CODE', trigger: 'blur' },
            {
                validator: (rule, value, callback) => {
                    if (value.toLowerCase() !== data.captchaCode.toLowerCase()) {
                        callback(new Error('验证码错误！'));
                    } else {
                        callback();
                    }
                },
                trigger: 'blur'
            }
        ]
    }
});

// === 1. 3D 视差卡片逻辑 ===
const handleMouseMove = (e) => {
    // 计算鼠标相对于屏幕中心的偏移量 (-1 到 1)
    const x = (e.clientX / window.innerWidth) * 2 - 1;
    const y = (e.clientY / window.innerHeight) * 2 - 1;
    mouseX.value = x;
    mouseY.value = y;
};

// 计算属性：根据鼠标位置生成 transform 样式
const cardStyle = computed(() => {
    const rotateX = -mouseY.value * 5; // 上下移动导致绕X轴旋转
    const rotateY = mouseX.value * 5;  // 左右移动导致绕Y轴旋转
    return {
        transform: `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`
    };
});

// === 2. 神经网络背景动画 (Canvas) ===
let animationFrameId;
const initNetwork = () => {
    const canvas = networkCanvas.value;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    // 自适应全屏
    const resize = () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', resize);
    resize();

    // 粒子类
    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.vx = (Math.random() - 0.5) * 0.5;
            this.vy = (Math.random() - 0.5) * 0.5;
            this.size = Math.random() * 2;
        }
        update() {
            this.x += this.vx;
            this.y += this.vy;
            // 边界反弹
            if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
            if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
        }
        draw() {
            ctx.fillStyle = 'rgba(0, 243, 255, 0.5)';
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    const particles = Array.from({ length: 60 }, () => new Particle());

    const animate = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        particles.forEach((p, index) => {
            p.update();
            p.draw();

            // 连线逻辑：距离近的粒子连线
            for (let j = index + 1; j < particles.length; j++) {
                const p2 = particles[j];
                const dx = p.x - p2.x;
                const dy = p.y - p2.y;
                const dist = Math.sqrt(dx*dx + dy*dy);

                if (dist < 150) {
                    ctx.strokeStyle = `rgba(0, 243, 255, ${0.2 * (1 - dist/150)})`;
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.stroke();
                }
            }

            // 鼠标交互：鼠标附近的粒子被“吸引”或连线
            // 这里为了性能简化为简单的连线
        });

        animationFrameId = requestAnimationFrame(animate);
    };
    animate();
};

// === 3. 科技感验证码 ===
const drawCaptcha = () => {
    const canvas = captchaCanvas.value;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 背景纹理
    ctx.fillStyle = '#0a101f';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // 网格线
    ctx.strokeStyle = '#1e3a5f';
    ctx.lineWidth = 1;
    for(let i=0; i<canvas.width; i+=10) {
        ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, canvas.height); ctx.stroke();
    }

    // 生成字符
    const chars = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ';
    let code = '';
    for (let i = 0; i < 4; i++) {
        const char = chars.charAt(Math.floor(Math.random() * chars.length));
        code += char;
        ctx.font = 'bold 22px "Courier New"';
        ctx.fillStyle = '#00f3ff';
        ctx.shadowBlur = 4;
        ctx.shadowColor = '#00f3ff';

        ctx.save();
        ctx.translate(15 + i * 22, 25);
        ctx.rotate((Math.random() - 0.5) * 0.4);
        ctx.fillText(char, 0, 0);
        ctx.restore();
    }
    data.captchaCode = code;
};

const refreshCaptcha = () => drawCaptcha();

// 生命周期
onMounted(() => {
    initNetwork();
    drawCaptcha();
});

onUnmounted(() => {
    cancelAnimationFrame(animationFrameId);
    window.removeEventListener('resize', () => {});
});

// 登录
const login = () => {
    formRef.value.validate((valid) => {
        if (valid) {
            isLoading.value = true;
            // 模拟API调用
            request.post('/login', data.form).then(res => {
                if (res.code === '200') {
                    ElMessage.success("登陆成功！");
                    localStorage.setItem('currentUser', JSON.stringify(res.data));
                    sessionStorage.setItem('user', JSON.stringify(res.data));
                    router.push('/');
                } else {
                    ElMessage.error(res.msg || "登录失败！");
                    refreshCaptcha();
                }
            }).catch(() => {
                // ElMessage.error("CONNECTION FAILURE");
            }).finally(() => {
                isLoading.value = false;
            });
        }
    });
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&display=swap');

/* 全局重置 */
.cyber-container {
    width: 100vw;
    height: 100vh;
    background-color: #050505;
    position: relative;
    overflow: hidden;
    font-family: 'Rajdhani', sans-serif; /* 科技感字体 */
    color: #fff;
    display: flex;
    justify-content: center;
    align-items: center;
}

/* === 背景层 === */
.bg-layer {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 0;
    background: radial-gradient(circle at center, #111b29 0%, #000 100%);
}

.network-canvas {
    position: absolute;
    top: 0;
    left: 0;
    z-index: 1;
    opacity: 0.6;
}

/* 装饰：旋转雷达 */
.radar-circle {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 800px;
    height: 800px;
    border: 1px dashed rgba(0, 243, 255, 0.1);
    border-radius: 50%;
    animation: rotate 60s linear infinite;
    z-index: 0;
}
.radar-circle::before {
    content: '';
    position: absolute;
    top: -1px;
    left: 50%;
    width: 10px;
    height: 10px;
    background: #00f3ff;
    box-shadow: 0 0 20px #00f3ff;
    border-radius: 50%;
}

/* 装饰：代码雨 */
.code-rain span {
    position: absolute;
    top: -50px;
    color: rgba(0, 243, 255, 0.2);
    font-size: 14px;
    writing-mode: vertical-rl;
    animation: rain 4s linear infinite;
    user-select: none;
}

/* === 登录视差容器 === */
.login-wrapper {
    position: relative;
    z-index: 10;
    /* 关键：视差效果由 JS 控制 transform */
    transition: transform 0.1s ease-out;
}

/* 登录框主体 */
.login-box {
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
    position: absolute;
    top: -2px; left: -2px; right: -2px; bottom: -2px;
    z-index: -1;
    background: linear-gradient(45deg, transparent 40%, #00f3ff 50%, transparent 60%);
    background-size: 200% 200%;
    animation: borderShine 4s linear infinite;
    opacity: 0.5;
}

/* HUD 四角瞄准器 */
.hud-corner {
    position: absolute;
    width: 15px;
    height: 15px;
    border: 2px solid #00f3ff;
    transition: all 0.3s ease;
}
.top-left { top: -1px; left: -1px; border-right: 0; border-bottom: 0; }
.top-right { top: -1px; right: -1px; border-left: 0; border-bottom: 0; }
.bottom-left { bottom: -1px; left: -1px; border-right: 0; border-top: 0; }
.bottom-right { bottom: -1px; right: -1px; border-left: 0; border-top: 0; }

/* 鼠标悬停时，四角向外扩张 */
.login-box:hover .top-left { transform: translate(-5px, -5px); }
.login-box:hover .top-right { transform: translate(5px, -5px); }
.login-box:hover .bottom-left { transform: translate(-5px, 5px); }
.login-box:hover .bottom-right { transform: translate(5px, 5px); }

/* 顶部扫描线 */
.scan-line {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 2px;
    background: #00f3ff;
    box-shadow: 0 0 10px #00f3ff;
    animation: scan 3s ease-in-out infinite;
    opacity: 0.5;
}

/* 头部样式 */
.header {
    text-align: center;
    margin-bottom: 30px;
}
.logo-area {
    display: flex;
    justify-content: center;
    margin-bottom: 15px;
}
.hex-bg {
    width: 60px;
    height: 60px;
    background: rgba(0, 243, 255, 0.1);
    clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
    display: flex;
    justify-content: center;
    align-items: center;
    border: 1px solid rgba(0, 243, 255, 0.3);
}
.logo-icon {
    color: #00f3ff;
    filter: drop-shadow(0 0 5px #00f3ff);
}
.title {
    font-size: 28px;
    letter-spacing: 4px;
    margin: 0;
    text-transform: uppercase;
    font-weight: 700;
}
.highlight { color: #00f3ff; }
.subtitle {
    font-size: 12px;
    color: #6a85a0;
    margin-top: 5px;
    letter-spacing: 1px;
}

/* 输入框交互增强 */
.input-group {
    position: relative;
    width: 100%;
}
.input-focus-border {
    position: absolute;
    bottom: 0;
    left: 50%;
    width: 0;
    height: 2px;
    background: #00f3ff;
    transition: all 0.4s ease;
    box-shadow: 0 0 10px #00f3ff;
    z-index: 2;
}
/* 深度选择器覆盖 Element 样式 */
:deep(.cyber-input .el-input__wrapper) {
    background-color: rgba(0, 0, 0, 0.3) !important;
    box-shadow: none !important;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 0;
    padding-left: 15px;
}
:deep(.cyber-input .el-input__wrapper.is-focus) {
    border-color: rgba(0, 243, 255, 0.5);
    background-color: rgba(0, 243, 255, 0.05) !important;
}
/* 输入框聚焦时，底部光条展开 */
:deep(.cyber-input .el-input__wrapper.is-focus) + .input-focus-border {
    width: 100%;
    left: 0;
}
:deep(.el-input__inner) {
    color: #fff !important;
    font-family: 'Rajdhani', sans-serif;
    letter-spacing: 1px;
    height: 40px;
}
:deep(.el-input__prefix-inner) {
    color: #00f3ff;
}

/* 下拉框特殊处理 */
:deep(.cyber-select .el-input__wrapper) {
    background-color: rgba(0, 0, 0, 0.3) !important;
    box-shadow: none !important;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 0;
}

/* 验证码行 */
.captcha-row {
    display: flex;
    gap: 15px;
    align-items: stretch;
}
.cyber-input.small {
    /* 调整输入框的宽度，给验证码图片留出空间 */
    width: 230px;
}
.captcha-box {
    position: relative;
    border: 1px solid rgba(0, 243, 255, 0.3);
    cursor: pointer;
    overflow: hidden;
    transition: all 0.3s;
}
.captcha-box:hover {
    border-color: #00f3ff;
    box-shadow: 0 0 10px rgba(0, 243, 255, 0.2);
}
/* 故障艺术效果覆盖层 */
.glitch-overlay {
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background: repeating-linear-gradient(
            transparent 0px,
            transparent 2px,
            rgba(0, 243, 255, 0.1) 3px,
            transparent 4px
    );
    pointer-events: none;
}

/* 按钮样式 - 能量填充效果 */
.cyber-btn {
    width: 100%;
    height: 50px;
    background: transparent !important;
    border: 1px solid #00f3ff !important;
    color: #00f3ff !important;
    position: relative;
    overflow: hidden;
    transition: all 0.3s;
    border-radius: 0;
}
.cyber-btn::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 100%; height: 100%;
    background: #00f3ff;
    transition: left 0.4s ease;
    z-index: 0;
}
.cyber-btn:hover::before {
    left: 0;
}
.cyber-btn:hover {
    color: #000 !important;
    box-shadow: 0 0 20px rgba(0, 243, 255, 0.4);
}
.btn-content {
    position: relative;
    z-index: 1;
    display: flex;
    justify-content: space-between;
    width: 100%;
    padding: 0 20px;
    font-weight: 700;
    letter-spacing: 2px;
}

/* 底部状态栏 */
.status-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 25px;
    padding-top: 15px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    font-size: 12px;
    color: #4a5d73;
}
.status-dot {
    width: 8px; height: 8px;
    background: #0f0;
    border-radius: 50%;
    margin-right: 5px;
    box-shadow: 0 0 5px #0f0;
    display: inline-block;
}
.reg-link {
    color: #6a85a0;
    text-decoration: none;
    transition: color 0.3s;
}
.reg-link:hover {
    color: #00f3ff;
}

/* 动画定义 */
@keyframes rotate {
    100% { transform: translate(-50%, -50%) rotate(360deg); }
}
@keyframes rain {
    100% { top: 100%; opacity: 0; }
}
@keyframes borderShine {
    0% { background-position: 0% 50%; }
    100% { background-position: 100% 50%; }
}
@keyframes scan {
    0% { top: 0%; opacity: 0; }
    50% { opacity: 1; }
    100% { top: 100%; opacity: 0; }
}
</style>
