class_names = []

# 打开categories.txt文件
with open("../yolov8/categories_200.txt", "r", encoding="utf-8") as file:
    for line in file:
        # 每行数据通过空格分隔
        parts = line.strip().split(" ")
        # 获取第二列的类别名称（从索引1开始）
        category_name = " ".join(parts[1:])  # 处理可能包含空格的类别名称
        class_names.append(category_name)

# 打印结果查看
print(class_names)
