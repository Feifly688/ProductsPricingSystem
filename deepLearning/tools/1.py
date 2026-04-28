from pycococreator import convert_coco_to_yolo

# 示例（需要根据你的路径调整）
convert_coco_to_yolo(
    images_dir="D:/datasets_200/images/train",           # 图片文件夹
    coco_json="D:/datasets_200/annotations/instances_train.json",
    output_dir="D:/datasets_200/labels"     # 输出 YOLO txt 标签文件夹
)