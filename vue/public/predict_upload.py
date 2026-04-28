import json
import os
import sys
import logging
import shutil
from ultralytics import YOLO
import time  # 导入time模块用于记录时间

# 临时修改日志记录级别，避免不必要的输出
logging.getLogger("ultralytics").setLevel(logging.WARNING)

# 获取当前脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
# 加载类别映射
categories = {}
categories_path = os.path.join(script_dir, 'categories_200.txt')
with open(categories_path, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line:
            parts = line.split(maxsplit=1)
            if len(parts) >= 2:
                cat_id = int(parts[0])
                name = parts[1]
                categories[cat_id] = name

# 加载模型
model_path = os.path.join(script_dir, 'best.pt')
model = YOLO(model_path)

# 接收图片路径参数
image_path = sys.argv[1]
# image_path = "../src/test/images/20180831-14-48-54-2406.jpg"

# 设置保存路径
save_dir = os.path.join(script_dir, 'runs')
public_save_dir = os.path.join(script_dir, 'results', 'images')

# 检查保存路径是否存在，如果存在则删除
if os.path.exists(save_dir):
    shutil.rmtree(save_dir)
os.makedirs(save_dir)
# 记录代码开始运行时间
start_run_time = time.time()

# 预测
results = model.predict(
    source=image_path,
    save=True,
    conf=0.8,
    project=os.path.join(script_dir, 'runs'),
    name='predict'
)

# 复制预测结果到 public/results/images 目录
predict_dir = os.path.join(save_dir, 'predict')
for root, dirs, files in os.walk(predict_dir):
    for file in files:
        src_file = os.path.join(root, file)
        dst_file = os.path.join(public_save_dir, file)
        shutil.copy2(src_file, dst_file)

# 记录代码结束运行时间
end_run_time = time.time()
# 计算代码运行时间
run_duration = end_run_time - start_run_time

# 获取推理时间
inference_time = results[0].speed['inference']

# 构建检测结果
detections = []
for result in results:
    counts = {}
    if result.boxes:
        cls_ids = result.boxes.cls.cpu().numpy().astype(int)
        for cls_id in cls_ids:
            counts[cls_id] = counts.get(cls_id, 0) + 1
    # 转换为商品列表
    for cls_id, count in counts.items():
        detections.append({
            "name": categories.get(cls_id, f"未知商品{cls_id}"),
            "count": int(count)
        })

# 获取保存后的图片名
file_name = os.path.basename(image_path)

# 构造符合前端期望的数据结构
response_data = {
    "code": "200",
    "data": detections,
    "file_name": file_name,  # 获取上传后的图片名称
    "inference_time": inference_time,  # 模型推理用时
    "run_duration": run_duration  # 代码运行用时
}

# 输出 JSON 结果
print(json.dumps(response_data))
