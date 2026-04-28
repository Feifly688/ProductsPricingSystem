import json
import os

# 定义 JSON 文件路径和训练图像文件夹路径
# json_file = '../datas/annotations/instances_train.json'
# train_folder = '../datas/images/train'
# labels_folder = '../datas/labels/train'
# json_file = '../datas/annotations/instances_val.json'
# train_folder = '../datas/images/val'
# labels_folder = '../datas/labels/val'
json_file = '../datas/annotations/instances_test.json'
train_folder = '../datas/images/test'
labels_folder = '../datas/labels/test'

# 创建 labels 文件夹（如果不存在）
if not os.path.exists(labels_folder):
    os.makedirs(labels_folder)

# 读取 JSON 文件
with open(json_file, 'r') as f:
    data = json.load(f)

# 构建类别 ID 到索引的映射
category_id_to_index = {category['id']: i for i, category in enumerate(data['categories'])}

# 处理每个图像
for image in data['images']:
    image_id = image['id']
    file_name = image['file_name']
    width = image['width']
    height = image['height']

    # 找到该图像的所有标注
    annotations = [ann for ann in data['annotations'] if ann['image_id'] == image_id]

    # 创建对应的 YOLO 标注文件
    label_file_name = os.path.splitext(file_name)[0] + '.txt'
    label_file_path = os.path.join(labels_folder, label_file_name)

    with open(label_file_path, 'w') as f:
        for ann in annotations:
            category_id = ann['category_id']
            bbox = ann['bbox']

            # 计算 YOLO 格式的标注信息
            x_center = (bbox[0] + bbox[2] / 2) / width
            y_center = (bbox[1] + bbox[3] / 2) / height
            w = bbox[2] / width
            h = bbox[3] / height

            # 获取类别索引
            category_index = category_id_to_index[category_id]

            # 写入标注信息
            f.write(f'{category_index} {x_center} {y_center} {w} {h}\n')

print('转换完成！')