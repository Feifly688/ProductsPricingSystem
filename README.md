# Products Pricing System

基于 Vue 3、Spring Boot 和 YOLOv8 的商品检测计价系统。系统支持商品信息管理、用户/管理员登录、商品图片检测、自动计价、计价记录保存与历史查询，适合用于超市商品识别和价格统计场景。

## 功能概览

- 商品检测计价：上传商品图片后调用 YOLOv8 检测脚本，返回商品类别、数量、检测结果图和总价。
- 商品管理：维护商品图片、名称、价格、销量等基础数据。
- 用户与管理员：支持登录、注册、权限路由和后台管理页面。
- 计价记录：保存每次检测结果、总价、商品明细和检测耗时。
- 数据可视化：提供首页统计、对比分析和价格历史等管理视图。

## 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 前端 | Vue 3 + Vite + Element Plus + Axios + ECharts | 3.3+ |
| 后端 | Spring Boot + MyBatis + MySQL | 3.3+ / 3.0.3 |
| AI 检测 | Python — YOLOv8 (Ultralytics) + PyTorch + OpenCV | Py 3.10+ |
| 部署 | 1Panel / OpenResty / Docker / 裸机 | — |

## 项目结构

```text
ProductsPricingSystem/
├── deepLearning/                   # 深度学习训练、预测脚本和模型相关代码
│   └── yolov8/
│       ├── predict_upload.py        # 后端调用的商品检测脚本
│       ├── categories_200.txt       # 类别映射
│       └── requirements.txt         # Python 推理依赖
├── files/                          # 商品图片等静态资源（需 Git LFS 或手动部署）
├── springboot/                     # Spring Boot 后端
│   └── src/main/
│       ├── java/com/example/       # 业务代码（controller / service / mapper / entity）
│       └── resources/              # 配置文件 + MyBatis XML
├── vue/                            # Vue 前端
│   ├── src/                        # 页面、路由、组件
│   ├── .env.development            # 开发环境变量
│   └── .env.production             # 生产环境变量
└── product_pricing_system.sql      # 数据库结构与初始数据
```

---

## 配置说明

### 后端配置（Spring Boot）

配置文件位于 `springboot/src/main/resources/`：

| 文件 | 用途 | 激活方式 |
|------|------|----------|
| `application.yml` | 公共配置（上传限制、MyBatis、检测超时） | 始终加载 |
| `application-dev.yml` | 开发环境（本地 MySQL、Python、文件路径） | `spring.profiles.active=dev` |
| `application-prod.yml` | 生产环境（服务器 MySQL、Python venv、文件路径） | `spring.profiles.active=prod` |

#### 开发环境 — 需要修改的关键字段

```yaml
# application-dev.yml
spring:
  datasource:
    username: root              # ← 改成你的 MySQL 用户名
    password: root              # ← 改成你的 MySQL 密码
    url: jdbc:mysql://localhost:3306/product_pricing_system?useSSL=false

file:
  storage-dir: /path/to/your/files      # ← 修改为本地存放商品图片的目录

model:
  base-path: /path/to/your/models       # ← 修改为存放 .pt 权重的目录

python:
  executable: python                     # ← 或 conda run -n yolov8 python
  script:
    path: /path/to/predict_upload.py    # ← 改为你的检测脚本绝对路径

temp:
  image:
    dir: /path/to/temp_upload_images    # ← 临时图片目录
```

#### 生产环境 ⚠️ 安全须知

**务必修改以下敏感项：**

1. **数据库密码** — 使用强密码，不要写死明文，推荐通过环境变量注入：

```yaml
# application-prod.yml
spring:
  datasource:
    password: ${DB_PASSWORD}           # 通过环境变量注入
```

启动时：`DB_PASSWORD=yourStrongPwd mvn spring-boot:run`

2. **CORS 域名** — 限制为实际的前端域名：

```yaml
app:
  cors:
    allowed-origins:
      - https://your-domain.com
```

3. **文件路径** — 和服务器实际路径保持一致。

### 前端配置（Vue + Vite）

```bash
# vue/.env.development
VITE_API_BASE_URL=http://localhost:9090/api   # 后端接口地址
VITE_DEV_SERVER_PORT=9091                     # 开发服务器端口
VITE_DEV_PROXY_TARGET=http://localhost:9090   # 代理目标
```

```bash
# vue/.env.production
VITE_API_BASE_URL=/api                        # 生产用相对路径（通过 Nginx 反向代理）
```

---

## 部署流程

### 方式一：裸机部署（推荐）

#### 1. 服务器环境准备

```bash
# 安装 JDK 17+
sudo apt install openjdk-17-jdk

# 安装 MySQL 8.0+
sudo apt install mysql-server-8.0

# 安装 Python 3.10+
sudo apt install python3.10 python3.10-venv

# 安装 Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs
```

#### 2. 初始化数据库

```bash
# 登录 MySQL 创建数据库
mysql -u root -p -e "CREATE DATABASE product_pricing_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;"

# 导入表结构 + 初始数据
mysql -u root -p product_pricing_system < product_pricing_system.sql
```

#### 3. 配置 Python 推理环境

```bash
cd /opt/projects/ProductsPricingSystem
python3.10 -m venv python/venv
source python/venv/bin/activate
pip install --upgrade pip
pip install -r deepLearning/yolov8/requirements.txt
```

将训练好的模型权重文件 `.pt` 放入 `python/models/` 目录。

#### 4. 构建并启动后端

```bash
cd springboot

# 使用环境变量传递数据库密码（⚠️ 不要写死在 yml 中）
export DB_PASSWORD=yourStrongPwd
export FILE_STORAGE_DIR=/opt/projects/ProductsPricingSystem/files
export MODEL_BASE_PATH=/opt/projects/ProductsPricingSystem/python/models
export PYTHON_SCRIPT_PATH=/opt/projects/ProductsPricingSystem/python/predict_upload.py

# 构建
mvn clean package -DskipTests

# 启动（生产模式）
java -jar target/springboot-0.0.1-SNAPSHOT.jar \
  -Dspring.profiles.active=prod \
  -DDB_PASSWORD=$DB_PASSWORD
```

建议使用 systemd 服务托管：

```ini
# /etc/systemd/system/product-pricing.service
[Unit]
Description=Products Pricing System Backend
After=network.target

[Service]
Type=simple
User=deploy
WorkingDirectory=/opt/projects/ProductsPricingSystem/springboot
Environment=DB_PASSWORD=yourStrongPwd
ExecStart=/usr/bin/java -jar /opt/projects/ProductsPricingSystem/springboot/target/springboot-0.0.1-SNAPSHOT.jar -Dspring.profiles.active=prod
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable product-pricing
sudo systemctl start product-pricing
```

#### 5. 构建并部署前端

```bash
cd vue
npm install
npm run build         # 产物在 vue/dist/
```

将 `vue/dist/` 目录下的文件部署到 Nginx 静态目录。

#### 6. Nginx 反向代理配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    root /opt/projects/ProductsPricingSystem/vue/dist;
    index index.html;

    # 前端路由（SPA）
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:8081/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }

    # 静态文件
    location /files/ {
        alias /opt/projects/ProductsPricingSystem/files/;
    }

    # 检测结果图片
    location /results/ {
        alias /opt/projects/ProductsPricingSystem/python/results/;
    }
}
```

配置 HTTPS（推荐）：

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

### 方式二：Docker 部署（可选）

项目根目录可创建 `docker-compose.yml`：

```yaml
version: '3.8'
services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_PASSWORD}
      MYSQL_DATABASE: product_pricing_system
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./product_pricing_system.sql:/docker-entrypoint-initdb.d/init.sql

  backend:
    build: ./springboot
    ports:
      - "8081:8081"
    environment:
      - DB_PASSWORD=${DB_PASSWORD}
      - SPRING_PROFILES_ACTIVE=prod
    depends_on:
      - mysql
    volumes:
      - ./files:/opt/projects/ProductsPricingSystem/files
      - ./deepLearning:/opt/projects/ProductsPricingSystem/python

  frontend:
    build: ./vue
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  mysql_data:
```

---

## 安全注意事项 ⚠️

部署前请务必处理以下安全问题：

### 严重（必须修复）

| 问题 | 影响 | 修复建议 |
|------|------|----------|
| 数据库密码明文 | 泄露即被拖库 | 使用环境变量 `DB_PASSWORD` 注入，**不要**写在 `application-prod.yml` 中 |
| API 无鉴权 | 任何人都可增删改查 | 添加 Spring Boot Interceptor 校验 session/token；敏感接口加角色注解 |
| 密码明文存储 | 数据库泄露后密码全裸 | 使用 `BCryptPasswordEncoder` 对密码哈希存储 |
| 文件上传穿越 | 可上传恶意文件到任意目录 | 对文件名做白名单校验：`FileUtil.cleanPath()` + 随机 UUID 重命名 |
| 本地路径泄漏 | 暴露开发者目录结构 | `application-dev.yml` 不应提交到 Git，或使用相对路径 + 占位符 |

### 中危（建议修复）

| 问题 | 建议 |
|------|------|
| 默认密码 `"1"` | 注册/创建用户时强制要求设置密码，或发送随机密码重置邮件 |
| 无密码复杂度 | 增加校验：至少 8 位，含字母+数字 |
| CORS 过于宽松 | `allowed-origins` 限定具体域名，不要用 `*` |

### 低危（可选修复）

| 问题 | 建议 |
|------|------|
| `useSSL=false` | 生产环境开启 SSL/TLS 连接 |
| `allowPublicKeyRetrieval=true` | 生产环境移除该配置 |

---

## 本地运行（快速开始）

### 1. 初始化数据库

```sql
CREATE DATABASE product_pricing_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
```

```bash
mysql -uroot -proot product_pricing_system < product_pricing_system.sql
```

### 2. 配置 Python 检测环境

```bash
cd deepLearning/yolov8
python -m venv venv
venv/bin/pip install --upgrade pip
venv/bin/pip install -r requirements.txt
```

模型权重文件（`best.pt`、`*.pt`、`*.pth`）需自行放置到 `deepLearning/models/` 对应目录。

### 3. 修改后端开发配置

编辑 `springboot/src/main/resources/application-dev.yml`，修改以下字段：

```yaml
spring:
  datasource:
    username: root                # MySQL 用户名
    password: root                # MySQL 密码

file:
  storage-dir: D:/your-project/files    # 改为你的 files 目录

model:
  base-path: D:/your-project/deepLearning/models

python:
  executable: python
  script:
    path: D:/your-project/deepLearning/yolov8/predict_upload.py

temp:
  image:
    dir: D:/your-project/temp_upload_images
```

### 4. 启动后端

```bash
cd springboot
mvn spring-boot:run -Dspring-boot.run.profiles=dev
```

后端默认地址：`http://localhost:9090/api`

### 5. 启动前端

```bash
cd vue
npm install
npm run dev
```

前端默认地址：`http://localhost:9091`

--- 

## 常见问题

**Q: 启动后端报数据库连接失败？**
A: 检查 MySQL 服务是否运行，`application-dev.yml` 中的用户名密码是否正确。

**Q: 检测提示 "Python 检测脚本不存在"？**
A: 确认 `python.script.path` 配置指向了正确的 `predict_upload.py` 文件路径。

**Q: `best.pt` 在哪里下载？**
A: 模型权重不纳入 Git 仓库，需自行训练或从 Ultralytics 官网下载预训练模型。

**Q: 生产环境如何修改数据库密码？**
A: 使用环境变量 `DB_PASSWORD`，不要改 `application-prod.yml` 文件内容。


