# Products Pricing System

基于 Vue 3、Spring Boot 和 YOLOv8 的商品检测计价系统。系统支持商品信息管理、用户/管理员登录、商品图片检测、自动计价、计价记录保存与历史查询，适合用于超市商品识别和价格统计场景。

## 功能概览

- 商品检测计价：上传商品图片后调用 YOLOv8 检测脚本，返回商品类别、数量、检测结果图和总价。
- 商品管理：维护商品图片、名称、价格、销量等基础数据。
- 用户与管理员：支持登录、注册、权限路由和后台管理页面。
- 计价记录：保存每次检测结果、总价、商品明细和检测耗时。
- 数据可视化：提供首页统计、对比分析和价格历史等管理视图。

## 技术栈

- 前端：Vue 3、Vite、Element Plus、Axios、ECharts
- 后端：Spring Boot 3、MyBatis、MySQL
- 检测：Python、YOLOv8、Ultralytics、PyTorch、OpenCV
- 部署：1Panel / OpenResty / Docker 可选

## 项目结构

```text
ProductsPricingSystem/
├── deepLearning/                 # 深度学习训练、预测脚本和模型相关代码
│   └── yolov8/
│       ├── predict_upload.py      # 后端调用的商品检测脚本
│       ├── categories_200.txt     # 类别映射
│       └── requirements.txt       # Python 推理依赖
├── files/                        # 商品图片等静态资源
├── springboot/                   # Spring Boot 后端
│   ├── src/main/java/
│   └── src/main/resources/
├── vue/                          # Vue 前端
│   ├── src/
│   ├── .env.development
│   └── .env.production
└── product_pricing_system.sql     # 数据库初始化脚本
```

## 本地运行

### 1. 初始化数据库

创建 MySQL 数据库：

```sql
CREATE DATABASE product_pricing_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
```

然后导入：

```bash
mysql -uroot -proot product_pricing_system < product_pricing_system.sql
```

本地默认后端配置见：

```text
springboot/src/main/resources/application-dev.yml
```

默认数据库连接：

```yaml
username: root
password: root
url: jdbc:mysql://localhost:3306/product_pricing_system
```

### 2. 配置 Python 检测环境

进入 YOLOv8 目录：

```bash
cd deepLearning/yolov8
```

创建并安装依赖：

```bash
python -m venv venv
venv\Scripts\pip install --upgrade pip
venv\Scripts\pip install -r requirements.txt
```

也可以使用 Conda 环境，开发配置中默认环境名为：

```yaml
conda:
  env:
    name: yolov8
```

注意：模型权重文件如 `best.pt`、`*.pt`、`*.pth` 未纳入 Git 仓库，需要自行放置到对应目录。

### 3. 启动后端

在 IntelliJ IDEA 中启动 `SpringbootApplication`，或执行：

```bash
cd springboot
mvn spring-boot:run -Dspring-boot.run.profiles=dev
```

本地后端默认地址：

```text
http://localhost:9090/api
```

### 4. 启动前端

```bash
cd vue
npm install
npm run dev
```

本地前端默认地址：

```text
http://localhost:9091
```

开发环境接口配置：

```text
vue/.env.development
```

生产环境接口配置：

```text
vue/.env.production
```

生产环境推荐使用相对路径：

```env
VITE_API_BASE_URL=/api
```

## 生产部署要点

推荐访问结构：

```text
https://feifly.me       前端静态站点
https://feifly.me/api   Spring Boot 后端接口
```

OpenResty / Nginx 关键配置：

```nginx
location / {
  try_files $uri $uri/ /index.html;
}

location /api/ {
  proxy_pass http://127.0.0.1:8081/api/;
  proxy_set_header Host $host;
  proxy_set_header X-Real-IP $remote_addr;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

生产后端配置见：

```text
springboot/src/main/resources/application-prod.yml
```

部署时需要确认：

- `server.servlet.context-path` 为 `/api`
- 前端生产包请求地址为 `/api`
- OpenResty 对 Vue history 路由配置了 `try_files`
- Python 脚本路径、虚拟环境路径、模型权重路径在服务器中真实存在
- MySQL 地址与容器网络模式匹配

## Git 说明

仓库已忽略以下内容：

- `node_modules/`
- `springboot/target/`
- `vue/dist/`
- Python 虚拟环境
- 临时上传目录和推理结果目录
- 大模型权重文件：`*.pt`、`*.pth`

如果需要部署检测功能，请手动准备模型权重和 Python 环境。

## 常见问题

### 前端刷新 `/login`、`/register` 出现 404

前端使用 Vue Router history 模式，OpenResty / Nginx 需要配置：

```nginx
location / {
  try_files $uri $uri/ /index.html;
}
```

### 登录一直转圈

优先检查：

- 浏览器 Network 中请求是否为 `/api/login`
- OpenResty `/api/` 是否正确反代到后端
- 后端是否能连接 MySQL
- `application-prod.yml` 是否被实际加载

### 商品检测报 BigDecimal 解析错误

价格数据由 MyBatis 按商品名映射返回，后端需要从行数据中提取 `price` 字段后再计算总价。当前版本已处理该情况。

