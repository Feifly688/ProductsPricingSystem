import glob
import os
import random
from collections import defaultdict
from datetime import datetime

import cv2
import numpy as np
import torch
from PIL import Image, ImageFont, ImageDraw
from torchvision import models, transforms
from ultralytics import YOLO

# 设置设备
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# -------------------- 初始化YOLO分割模型 --------------------
yolo_model = YOLO("../../yolov8/runs/detect/train3/weights/best.pt")  # 使用分割模型

# -------------------- 初始化ResNet分类模型 --------------------
num_classes = 200

# 修正模型结构（必须与训练时完全一致）
classify_model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
classify_model.fc = torch.nn.Sequential(
    torch.nn.Dropout(p=0.5),
    torch.nn.Linear(classify_model.fc.in_features, 512),
    torch.nn.ReLU(),
    torch.nn.Linear(512, num_classes)
)
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
class_names = ['上好佳荷兰豆55g', '菜园小饼80g', '上好佳鲜虾片40g', '上好佳蟹味逸族40g', '妙脆角魔力炭烧味65g',
               '盼盼烧烤牛排味块105g', '上好佳鲜虾条40g', '上好佳洋葱圈40g', '上好佳日式鱼果海苔味50g',
               '奇多日式牛排味90g', '奇多美式火鸡味90g', '上好佳粟米条草莓味40g', '甘源蟹黄味瓜子仁75g',
               '惠宜开心果140g', '惠宜咸味花生350g', '惠宜腰果160g', '惠宜枸杞100g', '惠宜地瓜干228g',
               '惠宜泰国芒果干80g', '惠宜黄桃果干75g', '惠宜柠檬片65g', '新疆和田滩枣454g', '惠宜香菇100g',
               '惠宜桂圆干500g', '惠宜茶树菇200g', '豪雄单片黑木耳150g', '惠宜煮花生454g', '惠宜黄花菜100g',
               '洽洽凉茶瓜子150g', '洽洽奶香味瓜子150g', '车仔茶包绿茶50g', '车仔茶包红茶50g', '优乐美香芋味80g',
               '优乐美红豆奶茶65g', '欢泥冲调土豆粥25g', '江中猴姑早餐米稀40g', '永和豆浆甜豆浆粉210g',
               '立顿柠檬风味茶180g', '桂格多种莓果麦片40g', '荣怡谷麦加黑米味30g', '荣怡谷麦加红豆味30g',
               '今野香辣牛肉面112g', '今野老坛酸菜牛肉面118g', '今野红烧牛肉面114g', '合味道海鲜风味84g',
               '康师傅白胡椒肉骨面76g', '康师傅香辣牛肉面105g', '康师傅葱香排骨面108g', '康师傅藤椒牛肉面85g',
               '华丰鸡肉三鲜伊面87g', '康师傅黑胡椒牛排面104g', '五谷道场红烧牛肉面100g', '康师傅老坛酸菜牛肉面114g',
               'Aji泡芙饼干芒果菠萝味60g', '庆联蓝莓味夹心饼63g', '庆联凤梨味夹心饼63g', '庆联草莓味夹心饼63g',
               '嘉顿威化饼干草莓味50g', '嘉顿威化饼干柠檬味50g', '爱时乐香草牛奶味50g', '爱时乐巧克力味50g',
               '百力滋海苔味60g', '百力滋草莓牛奶味45g', '雀巢脆脆鲨80g', '纳宝帝巧克力味威化58g',
               '桂力地中海风味面包条50g', '康师傅妙芙巧克力味48g', '爱乡亲唱片面包90g', '达利园派草莓味单个装',
               'mini奥利奥55g', '农夫山泉矿泉水550ml', '怡宝矿泉水555ml', '可口可乐零度500ml', '可口可乐500ml',
               '百事可乐600ml', '芬达苹果味500ml', '芬达橙味500ml', '雪碧500ml', '喜力啤酒500ml', '百威啤酒600ml',
               '百事可乐330ml', '可口可乐330ml', '王老吉310ml', '茶派柚子绿茶500ml', '茶派玫瑰荔枝红茶500ml',
               '康师傅冰红茶250ml', '加多宝250ml', 'RIO果酒水蜜桃味275ml', 'RIO果酒蓝玫瑰威士忌味275ml',
               '牛栏山二锅头100ml', '哈尔滨啤酒330ml', '青岛啤酒330ml', '雪花啤酒330ml', '哈尔滨啤酒500ml',
               'KELER啤酒500ml', '百威啤酒500ml', 'QQ星全聪奶125ml', 'QQ星均膳奶125ml', '娃哈哈AD钙奶220g',
               '活力宝动力源105ml', '旺仔牛奶复原乳250ml', '伊利纯牛奶250ml', '维他低糖原味豆奶250ml',
               '百怡花生牛奶250ml', '惠宜原味豆奶250ml', '伊利优酸乳250ml', '伊利早餐奶250ml', '达利园桂圆莲子360g',
               '银鹭冰糖百合银耳280g', '喜多多什锦椰果567g', '都乐菠萝块567g', '都乐菠萝块234g', '银鹭薏仁红豆粥280g',
               '银鹭莲子玉米粥280g', '银鹭紫薯紫米粥280g', '银鹭椰奶燕麦粥280g', '银鹭黑糖桂圆280g', '梅林午餐肉340g',
               '珠江桥牌豆豉鱼150g', '古龙原味黄花鱼120g', '雄鸡标椰浆140ml', '德芙芒果酸奶巧克力42g',
               '德芙摩卡巴旦木巧克力43g', '德芙百香果白巧克力42g', 'MM花生牛奶巧克力豆40g', 'MM牛奶巧克力豆40g',
               '好时牛奶巧克力40g', '好时曲奇奶香白巧克力40g', '脆香米海苔白巧克力24g', '脆香米奶香白巧克力24g',
               '士力架花生夹心巧克力51g', '士力架燕麦花生夹心巧克力40g', '士力架辣花生夹心巧克力40g',
               '炫迈果味浪薄荷味37g', '炫迈果味浪柠檬味37g', '炫迈薄荷味21g', '炫迈葡萄味21g', '炫迈西瓜味21g',
               '炫迈葡萄味50g', '绿箭无糖薄荷糖茉莉花茶味34g', '绿箭5片装15g', '比巴卜棉花泡泡糖可乐味11g',
               '比巴卜棉花泡泡糖葡萄味11g', '星爆缤纷原果味25g', '阿尔卑斯焦香牛奶味硬糖45g',
               '阿尔卑斯牛奶软糖黄桃酸奶味47g', '阿尔卑斯牛奶软糖蓝莓酸奶味47g', '王老吉润喉糖28g',
               '伊利牛奶片蓝莓味32g', '熊博士口嚼糖草莓牛奶味52g', '彩虹糖原果味45g', '宝鼎天鱼陈酿米醋245ml',
               '恒顺香醋340ml', '太太乐鸡精200g', '家乐香菇鸡茸汤料41g', '惠宜辣椒粉15g', '惠宜生姜粉15g',
               '味好美椒盐20g', '海星加碘精制盐400g', '恒顺料酒500ml', '东古味极鲜酱油150ml', '东古一品鲜酱油150ml',
               '欣和六月鲜酱油160ml', '李施德林零度漱口水80ml', '舒肤佳纯白清香沐浴露100ml', '美涛定型啫喱水60ml',
               '清扬男士洗发露活力运动薄荷型50ml', '蓝月亮风清白兰洗衣液80g', '高露洁亮白小苏打180g', '高露洁冰爽180g',
               '舒亮皓齿白80g', '云南白药牙膏45g', '舒克宝贝儿童牙刷', '清风原木纯品金装100x3', '洁柔face150x3',
               '斑布100x3', '维达婴儿150x3', '心相印小黄人150x3', '清风原木纯品黑耀系列100x3', '洁云绒触感100x3',
               '舒洁至柔升级100x3', '心相印红悦100x3', '得宝100x3', '清风新韧纯品100x3', '金鱼100x3',
               '清风原木纯品100x3', '洁柔可湿水面纸加厚100x3', '维达立体美100x3', '洁柔手帕纸', '心相印小黄人手帕纸',
               '原色纸手帕纸', '心相印茶语手帕纸', '清风质感纯品手帕纸', '迪士尼笔记簿', '三角固体棒', '蓝色笔袋',
               '晨光拼吧小蜗牛修正带', 'TAIPAI液体胶', '马培德自粘标签', '东亚记号笔']


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


# -------------------- 主处理流程 --------------------
def process_image(image_path, save_dir):
    # 读取图像
    image = cv2.imread(image_path)
    image_name = os.path.basename(image_path).replace(".jpg", "")
    product_counts = defaultdict(int)

    # YOLO检测分割
    results = yolo_model(image)

    for result in results:
        # 获取检测信息
        boxes = result.boxes.xyxy.cpu().numpy()
        masks = result.masks.cpu().numpy().data if result.masks else None

        for j, box in enumerate(boxes):
            x1, y1, x2, y2 = map(int, box[:4])
            h, w = image.shape[:2]

            # 确保坐标在合理范围
            y1, y2 = max(0, y1), min(h, y2)
            x1, x2 = max(0, x1), min(w, x2)

            # 应用掩码分割
            if masks is not None:
                mask = (masks[j] > 0.5).astype("uint8")  # 确保 mask 为 uint8 类型

                # 确保 mask 大小与原图一致
                if mask.shape[:2] != (h, w):
                    mask = cv2.resize(mask, (w, h))

                # 取出感兴趣区域的掩码
                cropped_mask = mask[y1:y2, x1:x2]

                # 确保 cropped_mask 与 ROI 尺寸一致
                if cropped_mask.shape[:2] != (y2 - y1, x2 - x1):
                    cropped_mask = cv2.resize(cropped_mask, (x2 - x1, y2 - y1))

                # 执行 bitwise_and 操作
                cropped = cv2.bitwise_and(image[y1:y2, x1:x2], image[y1:y2, x1:x2], mask=cropped_mask)
            else:
                cropped = image[y1:y2, x1:x2]

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
    test_images = glob.glob("../../datasets/test/images/*.jpg")
    selected_images = random.sample(test_images, 50)
    # test_images = glob.glob("../../single_images/*.jpg")
    # selected_images = random.sample(test_images, 30)

    for img_path in selected_images:
        process_image(img_path, save_dir)
