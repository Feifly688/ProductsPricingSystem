import hashlib
import random
import urllib.parse

import requests

# 百度翻译 API 的相关信息
appid = '20250227002286528'  # APP ID
secretKey = 'vgh5dwq1H8k7pkwX942h'  # 密钥
api_url = 'http://api.fanyi.baidu.com/api/trans/vip/translate'


def translate(text):
    salt = random.randint(32768, 65536)
    sign = appid + text + str(salt) + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    params = {
        'appid': appid,
        'q': text,
        'from': 'en',
        'to': 'zh',
        'salt': salt,
        'sign': sign
    }
    encoded_params = urllib.parse.urlencode(params)
    full_url = api_url + '?' + encoded_params
    print("请求 URL:", full_url)  # 打印请求 URL
    response = requests.get(full_url)
    print("响应内容:", response.text)  # 打印响应内容
    result = response.json()
    if 'trans_result' in result:
        return result['trans_result'][0]['dst']
    else:
        return text


# 读取英文类别文件
with open('../yolo/categories_200.txt', 'r', encoding='utf-8') as file:
    english_categories = file.readlines()

# 翻译每个类别
chinese_categories = []
for category in english_categories:
    category = category.strip()
    translated = translate(category)
    chinese_categories.append(translated)

# 将翻译后的类别保存到新文件
with open('../categories_chinese.txt', 'w', encoding='utf-8') as file:
    for category in chinese_categories:
        file.write(category + '\n')

print("翻译完成，结果已保存到 categories_chinese.txt 文件中。")
