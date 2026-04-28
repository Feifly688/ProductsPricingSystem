import os

# 指定 Images 文件夹路径
images_folder = "../datasets/train/images"
# 定义保存结果的文件路径
output_file = "image_stats.txt"

result = []

# 获取所有文件夹名称并按序号排序
folder_names = os.listdir(images_folder)
folder_names.sort(key=lambda x: int(x.split(' ', 1)[0]) if x.split(' ', 1)[0].isdigit() else float('inf'))

# 遍历排序后的文件夹
for folder_name in folder_names:
    folder_path = os.path.join(images_folder, folder_name)

    # 跳过文件，只处理文件夹
    if not os.path.isdir(folder_path):
        continue

    # 分割文件夹名称，去掉序号（序号与名称以空格分隔，取空格后的部分）
    folder_name_parts = folder_name.split(" ", 1)
    if len(folder_name_parts) >= 2:
        folder_name_clean = folder_name_parts[1]
    else:
        folder_name_clean = folder_name

    # 计算文件夹内的图片数量
    image_count = len(os.listdir(folder_path))

    result.append((folder_name_clean, image_count))

try:
    # 打开文件以写入结果
    with open(output_file, 'w', encoding='utf-8') as f:
        for name, count in result:
            line = f"{name}:{count}\n"
            f.write(line)
    print(f"结果已成功保存到 {output_file}")
except Exception as e:
    print(f"保存文件时出现错误: {e}")
