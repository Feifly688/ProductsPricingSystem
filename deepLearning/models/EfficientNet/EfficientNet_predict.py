import os
from datetime import datetime
import cv2
import torch
import glob
import random
import numpy as np
from collections import defaultdict
from PIL import Image, ImageFont, ImageDraw
from torchvision import models, transforms
from torchvision.transforms import functional as F
from EfficientNet import EfficientNet

# 设置设备
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# -------------------- 初始化GooGLeNet分类模型 --------------------
num_classes = 200

# 修正模型结构（必须与训练时完全一致）
classify_model = EfficientNet(width_coefficient=1,depth_coefficient=1,num_classes=num_classes)
classify_model.load_state_dict(torch.load("train/best_model.pth", map_location=device), strict=False)
classify_model = classify_model.to(device)
classify_model.eval()

# -------------------- 数据预处理 --------------------
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# -------------------- 中文支持配置 --------------------
font_path = "simhei.ttf"
font_size = 20
font = ImageFont.truetype(font_path, font_size)

# -------------------- 商品类别名称 --------------------
class_names = ['上好佳鲜虾片40g', '上好佳日式鱼果海苔味50g', '上好佳粟米条草莓味40g', '洽洽奶香味瓜子150g',
               '优乐美香芋味80g', '大今野香辣牛肉面112g', '康师傅藤椒牛肉面85g', '百力滋草莓牛奶味45g',
               '农夫山泉矿泉水550ml', '怡宝矿泉水555ml', '可口可乐500ml', '百事可乐600ml', '芬达橙味500ml', '雪碧500ml',
               '喜力啤酒500ml', '百威啤酒600ml', '可口可乐330ml', '王老吉310ml', '茶派玫瑰荔枝红茶500ml',
               '牛栏山二锅头100ml', '青岛啤酒330ml', '雪花啤酒330ml', '娃哈哈AD钙奶220g', '旺仔牛奶复原乳250ml',
               '伊利纯牛奶250ml', '伊利优酸乳250ml', '银鹭冰糖百合银耳280g', '喜多多什锦椰果567g',
               '德芙摩卡巴旦木巧克力43g', '好时曲奇奶香白巧克力40g', '士力架花生夹心巧克力51g', '炫迈果味浪薄荷味37g',
               '炫迈薄荷味21g', '炫迈葡萄味50g', '绿箭无糖薄荷糖茉莉花茶味34g', '绿箭5片装15g',
               '阿尔卑斯焦香牛奶味硬糖45g', '伊利牛奶片蓝莓味32g', '熊博士口嚼糖草莓牛奶味52g', '彩虹糖原果味45g',
               '太太乐鸡精200g', '舒肤佳纯白清香沐浴露100ml', '蓝月亮风清白兰洗衣液80g', '高露洁冰爽180g',
               '云南白药牙膏45g', '得宝100x3', '清风原木纯品100x3', '洁柔手帕纸', '心相印茶语手帕纸',
               '晨光拼吧小蜗牛修正带']


# -------------------- 工具函数 --------------------
def create_run_dir(base_dir="predict"):
    """创建带时间戳的保存目录"""
    timestamp = "predict_" + datetime.now().strftime("%Y%m%d_%H%M")
    run_dir = os.path.join(base_dir, timestamp)
    os.makedirs(run_dir, exist_ok=True)
    return run_dir


def draw_chinese_text(image, text, position, color=(0, 255, 0)):
    """在图像上绘制中文文本"""
    pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    draw.text(position, text, font=font, fill=color)
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)


# 边缘检测和物体分割
def detect_objects(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    objects = []
    boxes = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        object_image = image[y:y + h, x:x + w]
        objects.append(object_image)
        boxes.append((x, y, x + w, y + h))
    return objects, boxes


# -------------------- 主处理流程 --------------------
def process_image(image_path, save_dir):
    # 读取图像
    image = cv2.imread(image_path)
    image_name = os.path.basename(image_path).replace(".jpg", "")
    product_counts = defaultdict(int)

    # 边缘检测分割
    objects, boxes = detect_objects(image)

    for j, (cropped, box) in enumerate(zip(objects, boxes)):
        x1, y1, x2, y2 = box
        h, w = image.shape[:2]

        # 确保坐标在合理范围
        y1, y2 = max(0, y1), min(h, y2)
        x1, x2 = max(0, x1), min(w, x2)

        # 分类预测
        pil_img = Image.fromarray(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))
        tensor_img = transform(pil_img).unsqueeze(0).to(device)

        with torch.no_grad():
            output = classify_model(tensor_img)
            pred_class = torch.argmax(output).item()

        # 更新统计和标注
        class_name = class_names[pred_class]
        product_counts[class_name] += 1

        # 绘制标注
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        image = draw_chinese_text(image, class_name, (x1, y1 - 25))

    # 保存结果
    save_txt = os.path.join(save_dir, f"{image_name}.txt")
    with open(save_txt, "w") as f:
        f.write(f"{image_name}.jpg\n")
        for product, count in product_counts.items():
            f.write(f"{product}: {count}个\n")

    save_img = os.path.join(save_dir, f"{image_name}_result.jpg")
    cv2.imwrite(save_img, image)
    print(f"处理完成: {image_path} -> {save_txt}, {save_img}")


# -------------------- 执行主程序 --------------------
if __name__ == "__main__":
    save_dir = create_run_dir()
    test_images = glob.glob("../../single_images/*.jpg")
    selected_images = random.sample(test_images, 30)
    for img_path in selected_images:
        process_image(img_path, save_dir)
