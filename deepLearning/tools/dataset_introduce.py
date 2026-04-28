import os
import warnings

import boxx
import pandas as pd

warnings.filterwarnings("ignore")

print(os.listdir("../../datas_yolo"))
print(
    "***********************************************************************************************************************************")
# # visualization train image (single image)
# train_image = imread(glob.glob("datas_yolo/images/train/*")[0])
# boxx.show(train_image)
# # visualization val/test image (checkout image)
# val_image = imread(glob.glob("datas_yolo/images/val/*")[0])
# boxx.show(val_image)
# test_image = imread(glob.glob(".datas_yolo/images/test/*")[0])
# boxx.show(test_image)

# Loading annotation files
train_js = boxx.loadjson('../../datas_yolo/instances_train.json')
val_js = boxx.loadjson('../../datas_yolo/instances_val.json')
test_js = boxx.loadjson('../../datas_yolo/instances_test.json')
# Visualization struct of instances_train.json
# These annotation files has similar struct as COCO Object Detection Dataset
boxx.tree(train_js, deep=1)
boxx.tree(val_js, deep=1)
boxx.tree(test_js, deep=1)

# Visualization struct of instances_test.json
from pprint import pprint

pprint(test_js['images'][0])
print(
    "***********************************************************************************************************************************")

# The Categories Data format
categories_df = pd.DataFrame(train_js['categories'])
print(categories_df)
print(
    "***********************************************************************************************************************************")
# 提取类别名称
category_names = categories_df['name'].tolist()

# 确保只取前 200 个类别
category_names = category_names[:200]

# 保存到文本文件
with open('../yolo/categories_200.txt', 'w', encoding='utf-8') as file:
    for category in category_names:
        file.write(category + '\n')

print("类别已保存到 categories_200.txt 文件中。")

# Statistic the RPC dataset in different split set
def statistic_rpc_json_dataset(js, split_name=None):
    '''
    statistic dataset, input a coco format json file, then print and return `boxx.Markdown` instance
    note: `boxx.Markdown` is a sub class of `pd.DataFrame`
    '''
    df = pd.DataFrame(js['annotations'])
    images = len(js['images'])
    objects = len(js['annotations'])

    object_number_per_image = df.groupby('image_id').id.count().mean()
    category_number_per_image = df.groupby('image_id').apply(
        lambda sdf: len(set(sdf.category_id))).mean()

    markdown_df = pd.DataFrame([dict(split_name=split_name,
                                     images=images, objects=objects,
                                     object_number_per_image=round(object_number_per_image, 2),
                                     category_number_per_image=round(category_number_per_image, 2))])
    markdown = boxx.Markdown(
        markdown_df[['split_name', 'images', 'objects', 'object_number_per_image', 'category_number_per_image', ]])
    # boxx.g()
    print(markdown)
    return markdown


statistic_rpc_json_dataset(train_js, 'train')
statistic_rpc_json_dataset(val_js, 'val')
statistic_rpc_json_dataset(test_js, 'test')
print(
    "***********************************************************************************************************************************")

# Statistic checkout(val+test) set
checkout_js = dict(images=test_js['images'] + val_js['images'],
                   annotations=test_js['annotations'] + val_js['annotations'])
statistic_rpc_json_dataset(checkout_js, 'checkout(val+test)')
print(
    "***********************************************************************************************************************************")

# Statistic checkout(val+test) sets for different clutters
for level in ["easy", "medium", "hard"]:
    level_images = filter(lambda d: d['level'] == level, test_js['images'] + val_js['images'])
    level_images = list(level_images)

    level_image_ids = set([d['id'] for d in level_images])
    level_annotations = list(
        filter(lambda d: d['image_id'] in level_image_ids, test_js['annotations'] + val_js['annotations']))

    level_js = dict(images=level_images, annotations=level_annotations)
    statistic_rpc_json_dataset(level_js, level)
print(
    "***********************************************************************************************************************************")
