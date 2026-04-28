# fix_categories.py
import yaml
import os


def fix_data_yaml():
    """修复data.yaml格式"""
    yaml_path = '../data.yaml'

    # 读取原文件
    with open(yaml_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 备份
    backup_path = yaml_path + '.backup'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ 已备份原文件到: {backup_path}")

    # 加载并修复
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # 修复names字段
    if 'names' in data and isinstance(data['names'], list):
        # 已经是列表，检查是否需要移除前缀
        new_names = []
        for item in data['names']:
            if isinstance(item, str) and ':' in item:
                # 移除 "数字: " 前缀
                parts = item.split(':', 1)
                if len(parts) == 2:
                    new_names.append(parts[1].strip())
                else:
                    new_names.append(item)
            else:
                new_names.append(item)
        data['names'] = new_names

    # 保存修复后的文件
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
    print(f"✅ 已修复data.yaml")

    # 同时生成categories_200.txt供Java使用
    txt_path = '/yolov8/categories_200.txt'
    with open(txt_path, 'w', encoding='utf-8') as f:
        for i, name in enumerate(data['names']):
            f.write(f"{i} {name}\n")
    print(f"✅ 已生成类别文件: {txt_path}")

    # 打印前10个类别验证
    print("\n📋 前10个类别:")
    for i in range(min(10, len(data['names']))):
        print(f"  {i}: {data['names'][i]}")


if __name__ == '__main__':
    fix_data_yaml()