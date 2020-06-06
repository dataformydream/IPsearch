import os
import sys
import requests
import json
from lxml import etree
import random
import threading, time, queue
from concurrent.futures import ThreadPoolExecutor, as_completed


class IPSearch:
    # 参数和设置
    def __init__(self, url, header_add=None, cookies=None):
        self.url = url
        self.cookies = cookies
        self._stop_message = queue.Queue()
        self.header_add = header_add
        self.proxies = {'http': [], 'https': []}
        self.del_proxies = {'http': [], 'https': []}
        self.root_url = ['https://www.xicidaili.com/nn/1',
                         'http://www.xiladaili.com/gaoni/',
                         'https://ip.jiangxianli.com/?page=1&country=%E4%B8%AD%E5%9B%BD']
        self.user_list = (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/75.0.3770.142 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3722.400 QQBrowser/10.5.3739.400',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/69.0.3497.100 Safari/537.36 QIHU 360EE',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/69.0.3947.100 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/76.0.3809.100 Safari/537.36 OPR/63.0.3368.43',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362',
            'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; LCTE; rv:11.0) like Gecko',
            'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/534.54.16 (KHTML, like Gecko) '
            'Version/5.1.4 Safari/534.54.16',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/55.0.2883.87 UBrowser/6.2.3964.2 Safari/537.36')

    # 随机代理，没有则返回None
    def random_proxy(self, proxy_type='all'):
        try:
            if proxy_type == 'all':
                select_proxies_pool = list(self.proxies['http'] + self.proxies['https'])  # 并集
                proxy = random.choice(select_proxies_pool)
                if 'https' in proxy:
                    proxy_dictionary = {'https': proxy}
                else:
                    proxy_dictionary = {'http': proxy}
            elif proxy_type == 'http':
                select_proxies_pool = self.proxies['http']
                proxy = random.choice(select_proxies_pool)
                proxy_dictionary = {'http': proxy}
            elif proxy_type == 'https':
                select_proxies_pool = self.proxies['https']
                proxy = random.choice(select_proxies_pool)
                proxy_dictionary = {'https': proxy}
            else:
                raise KeyError
        except Exception as e:
            print(f'未找到代理,使用本机IP：{e}')
            proxy_dictionary = None
        return proxy_dictionary

    # 随机请求头
    def random_header(self):
        # 设置头
        header = {"User-Agent": random.choice(self.user_list)}
        if self.header_add:
            for key, value in self.header_add.items():
                if hasattr(value, '__call__'):
                    header[key] = value()
                else:
                    header[key] = value
        return header

    # 请求方法，检查是否有referer ,x-sign等，也是消费者模型,保证请求成功为止
    def requests(self, url, proxy_type="all", timeout=5, cookies=None, header_add=None):
        succeed_flag = False
        headers = self.random_header()
        if not cookies:
            cookies = self.cookies
        if not header_add:
            header_add = self.header_add
        if header_add:
            for key, value in header_add.items():
                if hasattr(value, '__call__'):
                    headers[key] = value()
                else:
                    headers[key] = value
        while not succeed_flag:
            proxy_dictionary = self.random_proxy(proxy_type)
            try:
                response = requests.get(url, headers=headers, proxies=proxy_dictionary,
                                        cookies=cookies, timeout=timeout)
                response.encoding = response.apparent_encoding
                while not response:
                    time.sleep(1)
                    raise ValueError
                succeed_flag = True
                return response
            except Exception as e:
                # 失败则重新请求，同时更新列表
                time.sleep(1)
                print(f'error{e}')
                print('重新请求，已删去失败代理。')
                for key, value in proxy_dictionary.items():
                    self.proxies[key].remove(value)
                    self.del_proxies[key].append(value)

    # 备份到本地
    def ip_download(self, download_path=''):
        # print('正在备份到本地...')
        if download_path and not os.path.exists(download_path):
            os.makedirs(download_path)
        json_path = os.path.join(download_path, 'IP.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            download_list = [self.proxies, self.del_proxies]
            json.dump(download_list, f, indent=4, separators=(',', ':'))
        # print('备份完成')

    # 导入到IP池
    def ip_load(self, json_path=''):
        print(os.path.join(json_path, 'IP.json'))
        if os.path.exists(os.path.join(json_path, 'IP.json')):
            print('已发现本地代理，正在导入...')
            with open(os.path.join(json_path, 'IP.json'), 'r', encoding='utf-8') as f:
                ip_dictionary = json.load(f)
                print(ip_dictionary[0])
            self.proxies['http'] = ip_dictionary[0]['http']
            self.proxies['https'] = ip_dictionary[0]['https']
            self.del_proxies['http'] = ip_dictionary[1]['http']
            self.del_proxies['https'] = ip_dictionary[1]['https']
            print('本地代理已导入到IP池...')
        else:
            print('本地没有备份!')

    # 单个IP的验证函数
    def ip_test(self, url, proxy, timeout=1):
        if 'https' in proxy:
            proxy_dictionary = {'https': proxy}
        else:
            proxy_dictionary = {'http': proxy}
        headers = self.random_header()
        headers['Connection'] = 'close'
        try:
            response = requests.get(url, headers=headers, proxies=proxy_dictionary, cookies=self.cookies,
                                    timeout=timeout)
            response.raise_for_status()
            return True, proxy
        except:
            return False, proxy

    # 检查ip列表是否可用，多线程,若不输入要测试的列表，默认测试proxies和del_proxies全部一次
    def ip_list_test(self, url, test_list=None, workers=4, timeout=1):
        if not test_list:
            test_list_now = list(set(
                self.proxies['http'] + self.proxies['https'] + self.del_proxies['http'] + self.del_proxies['https']))
        else:
            test_list_now = test_list
        # 考虑初始为零的情况
        if len(test_list) != 0:
            print(f'要检测的IP共有{len(test_list_now)}个,开始测试...')
            print(f'开始验证IP对网站[{url}]是否有效,时间较长，请等待...')
            with ThreadPoolExecutor(max_workers=workers) as thread_pool:
                object_list = list()
                succeed_ip = list()
                failed_ip = list()
                for num in range(len(test_list)):
                    # print(proxy)
                    unit_object = thread_pool.submit(self.ip_test, url, test_list[num], timeout=timeout)
                    object_list.append(unit_object)
                num = 0
                for run_object in as_completed(object_list):
                    num += 1
                    result, pro = run_object.result()
                    if result:
                        sys.stdout.write(f"\r测试进度[%d/%d]： IP[{pro}]可用 " % (num, len(test_list)))

                        succeed_ip.append(pro)
                    else:
                        sys.stdout.write(f"\r测试进度[%d/%d]： IP[{pro}]失效" % (num, len(test_list)))
                        failed_ip.append(pro)
            print(f'\n{len(test_list)}个IP测试完成!可用IP为{len(succeed_ip)}个，失效IP为{len(failed_ip)}个')
            return succeed_ip, failed_ip
        else:
            return [], []

    # 更新函数，从网页获取到的ip列表，去重和检测后更新进proxies并保存到本地，也可重新检测并覆盖更新本地列表
    def update(self, un_test_list=None, re_update=False):
        choice_list = []
        # 判断是否覆盖更新
        if re_update:
            choice_list = list(set(
                self.proxies['http'] + self.proxies['https'] + self.del_proxies['http'] + self.del_proxies['https']))
            self.proxies['http'] = []
            self.proxies['https'] = []
            self.del_proxies['http'] = []
            self.del_proxies['https'] = []
        # 若更新，进行去重，判断IP是否已经在proxies中,返回新有的IP
        if un_test_list:
            for unit in un_test_list:
                if unit not in str(self.proxies) and unit not in str(self.del_proxies):
                    choice_list.append(unit)
        # 将去重后的IP进行检测
        succeed_ip, failed_ip = self.ip_list_test(self.url, test_list=choice_list)
        # 添加进IP池
        for unit_ip in succeed_ip:
            if 'https' in unit_ip:
                self.proxies['https'].append(unit_ip)
            else:
                self.proxies['http'].append(unit_ip)
        for unit_ip in failed_ip:
            if 'https' in unit_ip:
                self.del_proxies['https'].append(unit_ip)
            else:
                self.del_proxies['http'].append(unit_ip)
        self.ip_download()

    # 单独的请求西刺网站
    def get_xi_ci(self, url=None):
        if not url:
            url = self.root_url[0]
        pro_list = list()
        response = self.requests(url).text
        pro_text = etree.HTML(response).xpath("//tr[@class]")
        for num in pro_text:
            ip_number = num.xpath('./td[2]/text()')[0]
            port = num.xpath('./td[3]/text()')[0]
            types = num.xpath('./td[5]/text()')[0]
            type_url = num.xpath('./td[6]/text()')[0].lower()
            speed = float(num.xpath('.//div[@class="bar"]')[0].xpath('./@title')[0].replace('秒', ''))
            connect_speed = float(num.xpath('.//div[@class="bar"]')[1].xpath('./@title')[0].replace('秒', ''))
            life = num.xpath('./td[last()-1]/text()')[0]
            if types == '高匿' and speed < 2 and connect_speed < 1 and '天' in life or '小时' in life:  # 筛选条件，可自己添加
                pro = type_url + '://' + ip_number + ':' + port
                pro_list.append(pro)
        print(f'西刺获取成功，共有{len(pro_list)}个IP')
        return pro_list

    # 单独的请求西拉网站,有反爬
    def get_xi_la(self, url=None):
        pro_list = []
        # 西拉网站响应较慢，timeout设置时间较长
        headers = self.random_header()
        headers['Referer'] = 'http://www.xiladaili.com/'
        response = requests.get(url, headers=headers, timeout=None).text
        pro_text = etree.HTML(response).xpath("//tbody/tr")
        for num in pro_text:
            ip_number = num.xpath('./td[1]/text()')[0]
            types = num.xpath('./td[3]/text()')[0]
            type_url = num.xpath('./td[2]/text()')[0].replace('代理', '').lower()
            if 'https' in type_url:
                type_url = 'https'
            speed = float(num.xpath('./td[5]/text()')[0])
            life = num.xpath('./td[6]/text()')[0]
            score = int(num.xpath('./td[last()]/text()')[0])
            if '高匿' in types and speed < 3 or '天' in life and score > 10:  # 筛选条件，可自己添加
                pro = type_url + '://' + ip_number
                pro_list.append(pro)
        print(f'西拉获取成功，共有{len(pro_list)}个IP')
        return pro_list

    # 单独的请求免费代理库网站
    def get_free(self, url=None):
        pro_list = list()
        if not url:
            url = self.root_url[2]
        response = self.requests(url).text
        pro_text = etree.HTML(response).xpath("//tbody/tr")
        for num in pro_text:
            ip_number = num.xpath('./td[1]/text()')[0]
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
                pro = type_url + '://' + ip_number + ':' + port
                pro_list.append(pro)
        print(f'免费代理库获取成功，共有{len(pro_list)}个IP')
        return pro_list

    # 目前可用的IP数
    def number(self):
        succeed_http_number = len(self.proxies['http'])
        succeed_https_number = len(self.proxies['https'])
        failed_http_number = len(self.del_proxies['http'])
        failed_https_number = len(self.del_proxies['https'])
        return [succeed_http_number + succeed_https_number, failed_https_number + failed_http_number]

    # 获取IP列表并实时维护
    def search_realtime(self, need_number=30):
        self.ip_load()  # 查询本地并导入
        self.update(re_update=True)  # 检测一次
        # 定义一个实时线程类并行交互爬取IP
        out_class = self  # 继承外部类

        class SearchRealtime(threading.Thread):
            def __init__(self, message):
                super().__init__()
                self._queue = message
                self.out = out_class  # 导入外部类参数和方法

            def run(self):
                print(f"可用IP数为{self.out.number()[0]}")
                if self.out.number()[0] >= need_number:
                    print(f'本地IP数{self.out.number()[0]}已满足要求{need_number}，子线程休眠')
                while True:
                    page = [1, 1, 1]
                    while self.out.number()[0] < need_number:
                        print(f"子线程|可用IP数为{self.out.number()[0]},小于最低设置{need_number}，更新中...")
                        print(f'子线程|获取中：西刺第{page[0]}页...')
                        ip_list_0 = self.out.get_xi_ci(self.out.root_url[0] + str(page[0]))
                        self.out.update(ip_list_0)
                        page[0] += 1
                        # 不够则爬取另外网站
                        if self.out.number()[0] < need_number:
                            print(f"子线程|可用IP数为{self.out.number()[0]},小于最低设置{need_number}，更新中...")
                            print(f'子线程|获取中：免费代理库第{page[2]}页...')
                            ip_list_2 = self.out.get_free(self.out.root_url[2].replace('page=1', f'page={page[2]}'))
                            self.out.update(ip_list_2)
                            page[2] += 1
                        else:
                            print(f'本地IP数{self.out.number()[0]}已满足要求{need_number}，子线程休眠')
                            break
                        # 不够则爬取另外网站
                        if self.out.number()[0] < need_number:
                            print(f"子线程|可用IP数为{self.out.number()[0]},小于最低设置{need_number}，更新中...")
                            print(f'子线程|获取中：西拉第{page[1]}页...')
                            ip_list_1 = self.out.get_xi_la(self.out.root_url[1] + str(page[1]))
                            self.out.update(ip_list_1)
                            page[1] += 1
                        else:
                            print(f'本地IP数{self.out.number()[0]}已满足要求{need_number}，子线程休眠')
                            break
                    msg = self._queue.get()
                    if isinstance(msg, str) and msg == 'quit':
                        print(f"爬取成功,本地IP数{self.out.number()[0]}，停止维护IP池，结束子进程")
                        break

        search = SearchRealtime(self._stop_message)
        search.start()

    def stop_search(self):
        self.ip_download()
        self._stop_message.put('quit')


if __name__ == "__main__":
    test_url = 'https://www.baidu.com/'
    # test_url = 'https://www.ximalaya.com/'
    ip = IPSearch(test_url)
    ip.search_realtime(need_number=30)
    ip.stop_search()

