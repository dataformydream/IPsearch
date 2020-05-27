#!user/bin/env python
# -*- encoding=utf-8 -*-
import os
import requests
from lxml import etree
import json
import random

user_agent_list = [
    'Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.2.149.27 Safari/525.13'
    , 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36'
    , 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'
    , 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0'
    , 'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070803 Firefox/1.5.0.12'
    , 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36'
    , 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'
    , "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
      " AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/81.0.4044.138 Safari/537.36"
]
root_url = ['https://www.xicidaili.com/nn/1',
            'http://www.xiladaili.com/gaoni/',
            'https://ip.jiangxianli.com/?page=1&country=%E4%B8%AD%E5%9B%BD',
            ]
# proxies需要引用
proxies = []
header_add = {}


# 随机请求头
def random_header():
    # 设置头
    header = {"User-Agent": random.choice(user_agent_list)}
    for key, value in header_add.items():
        if hasattr(value, '__call__'):
            header[key] = value()
        else:
            header[key] = value
    return header


# 基本的网页请求函数,可通用
def get_response(url):
    global proxies
    succeed_flag = True
    while succeed_flag:
        if proxies:
            unit_pro = random.choice(proxies)
            if 'https' in unit_pro:
                pro = {'https': unit_pro}
            else:
                pro = {'http': unit_pro}
        else:
            unit_pro = None
            print("无代理,使用本机IP")
            pro = None
        try:
            response = requests.get(url, headers=random_header(), proxies=pro, timeout=None)
            response.encoding = response.apparent_encoding
            succeed_flag = False
            return response
        except:
            # 失败则重新请求，同时更新列表
            print('被识别！重新请求，已删去失败代理。')
            proxies.remove(unit_pro)


# 单独的请求西刺网站
def get_xici(url):
    pro_list = list()
    response = get_response(url).text
    pro_htmls = etree.HTML(response).xpath("//tr[@class]")
    for num in pro_htmls:
        ip = num.xpath('./td[2]/text()')[0]
        port = num.xpath('./td[3]/text()')[0]
        types = num.xpath('./td[5]/text()')[0]
        type_url = num.xpath('./td[6]/text()')[0].lower()
        speed = float(num.xpath('.//div[@class="bar"]')[0].xpath('./@title')[0].replace('秒', ''))
        connect_speed = float(num.xpath('.//div[@class="bar"]')[1].xpath('./@title')[0].replace('秒', ''))
        life = num.xpath('./td[last()-1]/text()')[0]
        if types == '高匿' and speed < 2 and connect_speed < 1 and '天' in life or '小时' in life:  # 筛选条件，可自己添加
            pro = type_url + '://' + ip + ':' + port
            pro_list.append(pro)
    print(f'西刺获取成功，共有{len(pro_list)}个IP')
    return pro_list


# 单独的请求西拉网站
def get_xila(url):
    pro_list = []
    response = get_response(url).text
    pro_htmls = etree.HTML(response).xpath("//tbody/tr")
    for num in pro_htmls:
        ip = num.xpath('./td[1]/text()')[0]
        types = num.xpath('./td[3]/text()')[0]
        type_url = num.xpath('./td[2]/text()')[0].replace('代理', '').lower()
        if 'https' in type_url:
            type_url = 'https'
        speed = float(num.xpath('./td[5]/text()')[0])
        life = num.xpath('./td[6]/text()')[0]
        score = int(num.xpath('./td[last()]/text()')[0])
        if '高匿' in types and speed < 3 or '天' in life and score > 10:  # 筛选条件，可自己添加
            pro = type_url + '://' + ip
            pro_list.append(pro)
    print(f'西拉获取成功，共有{len(pro_list)}个IP')
    return pro_list


# 单独的请求免费代理库网站
def get_mianfei(url):
    pro_list = list()
    response = get_response(url).text
    pro_htmls = etree.HTML(response).xpath("//tbody/tr")
    for num in pro_htmls:
        ip = num.xpath('./td[1]/text()')[0]
        port = num.xpath('./td[2]/text()')[0]
        types = num.xpath('./td[3]/text()')[0]
        type_url = num.xpath('./td[4]/text()')[0].lower()
        speed = num.xpath('./td[8]/text()')[0]
        if '毫秒' in speed:
            speed = float(speed.replace('毫秒', '')) / 1000
        else:
            speed = float(speed.replace('秒', ''))
        life = num.xpath('./td[last()-2]/text()')[0]
        if types == '高匿' and speed < 2 and '天' in life or '小时' in life:  # 筛选条件，可自己添加
            pro = type_url + '://' + ip + ':' + port
            # print(pro)
            pro_list.append(pro)
    print(f'免费代理库获取成功，共有{len(pro_list)}个IP')
    return pro_list


# 测试和筛选对输入网站是否可爬取
def add_test(url, test_list=None):
    global proxies
    if not test_list:
        test_list = proxies[:]
    print(f'开始验证对爬取网站{url}的有效性,时间较长，请等待...')
    print(test_list)
    for pro in test_list:
        try:
            if 'https' in pro:
                pro_dic = {'https': pro}
            else:
                pro_dic = {'http': pro}
            response = requests.get(url, headers=random_header(), proxies=pro_dic, timeout=1)
            response.raise_for_status()
            print('IP适用，已保存')
        except:
            print('已删去请求失败IP')
            test_list.remove(pro)
    print('测试完成，适用IP已添加到proxies')
    proxies = list(set(proxies + test_list))
    print(f'proxies已有ip为{len(proxies)}个。')
    with open('ip.json', 'w', encoding='utf-8') as f:
        json.dump(proxies, f, indent=4, ensure_ascii=False, separators=(',', ':'))


# 主函数
def search_proxies(url, need_number=30, test_flag=True):
    global proxies
    print('获取代理中...')
    if os.path.exists('ip.json'):
        with open('ip.json', 'r', encoding='utf-8') as f:
            proxies += json.loads(f.read())
        print(f'已导入本地备份,本地已有的代理为{len(proxies)}个')
        if test_flag:
            add_test(url)
            print(f'本地请求成功IP为{len(proxies)}个。')
    else:
        print('未发现本地IP文件，从免费代理网站重新获取...')
    if len(proxies) < need_number:
        print(f'离要求的IP数还差{need_number - len(proxies)}个，从免费代理网站开始获取')
        print('获取中：西刺')
        add_test(url, [i for i in get_xici(root_url[0]) if i not in proxies])  # 先筛选出不重复的，再检查
        while len(proxies) < need_number:
            print('可用IP不足,获取更多西拉和免费代理库IP：')
            page = 1
            new_ip = get_xila(root_url[1] + str(page)) + get_mianfei(
                root_url[2].replace('page=1', f'page={page}'))
            add_test(url, [i for i in new_ip if i not in proxies])
            print(f'成功获取第{page}页!')
            page += 1
        print(f'代理获取完毕，最终获取到{len(proxies)}个可用代理,已写入本地。')
        with open('ip.json', 'w', encoding='utf-8') as f:
            json.dump(proxies, f, indent=4, ensure_ascii=False, separators=(',', ':'))
    else:
        print('本地IP数已达到要求，暂不请求网站获取IP。')


if __name__ == "__main__":
    search_proxies('https://www.ximalaya.com/', 20)

