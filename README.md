# IPsearch
这是一个自动查找免费可用IP代理的python脚本，内部封装实现爬虫的前期工作。

## 第一版本

**IPSearch_0.py**

详细介绍请参考

### 使用方法

#### **1、引用**

```python
from IPSearch_0 import *
```

![点击并拖拽以移动](data:image/gif;base64,R0lGODlhAQABAPABAP///wAAACH5BAEKAAAALAAAAAABAAEAAAICRAEAOw==)

或者

```python
from IPSearch_0 import proxies,header_add,get_response,add_test,search_proxies
```

![点击并拖拽以移动](data:image/gif;base64,R0lGODlhAQABAPABAP///wAAACH5BAEKAAAALAAAAAABAAEAAAICRAEAOw==)

#### **2、各变量用途和用法** 

**proxies**

全局变量，代理池，列表类型，如：[ip1,ip2,ip3,...]，初始为空。

**header_add**

和请求头的设置有关，默认headers中只有随机选取的"User-Agent"这一项，要添加更多参数如下：

```python
from xm_sign import get_sign  # 要传入headers的函数
# 将要添加的参数新建键值对传入header_add
# 同时支持变量和函数传入，注意：传入函数时传入的是函数名get_sign，而不是函数get_sign()
header_add['xm-sign']=get_sign
header_add['Referer']='https://www.ximalaya.com/'
```

![点击并拖拽以移动](data:image/gif;base64,R0lGODlhAQABAPABAP///wAAACH5BAEKAAAALAAAAAABAAEAAAICRAEAOw==)

**get_response(url)**

封装后的request.get()函数，实现随机user-agent，随机proxies请求网页，若proxies为空则使用本地IP，若IP失效则从proxies中删去，直到请求成功为止。

输入：要请求网页的URL，返回值：request.get()返回类型，可用r.text,r.content等

```python
header_add['xm-sign']=get_sign
header_add['Referer']='https://www.ximalaya.com/'
# ----------------之前需要设置好添加的headers内容，get_response内部调用-----------------------
# get_response(url) 传入要爬取的网站即可，在函数内部实现代理的随机选取、
# 同时支持http和https代理、while语句保证请求成功和删除失效代理等
response = get_response('https://www.ximalaya.com/category/')
# 函数返回值即为requests.get()返回类型
print(response.text)
print(response.content)
print(response.status_code)
print(response.request.headers)
```

![点击并拖拽以移动](data:image/gif;base64,R0lGODlhAQABAPABAP///wAAACH5BAEKAAAALAAAAAABAAEAAAICRAEAOw==)

 **add_test(url,test_list=None)**

用来检测test_list中的代理，是否对URL可用（能否请求成功），可用则添加进proxies，若没有要检测的ip池可忽略。

输出：无，函数直接对proxies进行操作，同时新的proxies覆盖到本地json文件保存（ip.json，项目文件夹中生成）

```python
test_list=[ip1,ip2,ip3,.....]
# 测试test_list中ip是否可用并更新到proxies
add_test('http://www.baidu.com',test_list)
# 测试proxies中ip是否仍有效,不指定test_list
add_test('http://www.baidu.com')
```

![点击并拖拽以移动](data:image/gif;base64,R0lGODlhAQABAPABAP///wAAACH5BAEKAAAALAAAAAABAAEAAAICRAEAOw==)

**search_proxies(url,need_number=30,test_flag=True)**

 主函数，输入为要爬取网站的URL，需要的ip数量的最小值，test_flag为True时，本地之前保存的ip重新测试，为False时不测试，直接传入proxies

实现功能：

1、导入本地已有json测试并导入proxies。

2、文件数判断，获取ip到满足设置的need_number为止。

3、更新proxies和本地json文件

#### **3、完整使用方法**

```python
# 喜马拉雅获取xm_sign 的引用，get_sign()函数
from xm_sign import get_sign
from IPSearch_0 import proxies, header_add, get_response, add_test, search_proxies
header_add['xm-sign'] = get_sign
header_add['Referer'] = 'https://www.ximalaya.com/'
print(header_add)
search_proxies('https://www.ximalaya.com/', 20)
print(proxies)
'''
在此调用get_response()实现爬虫程序
response = get_response('https://www.ximalaya.com/category/')
# 可实时调用，补充代理池
search_proxies('https://www.ximalaya.com/', 100)
'''
```

### 输出示例

```python
{'xm-sign': <function get_sign at 0x000001BFBBA99AF0>, 'Referer': 'https://www.ximalaya.com/'}
获取代理中...
未发现本地IP文件，从免费代理网站重新获取...
离要求的IP数还差20个，从免费代理网站开始获取
获取中：西刺
无代理,使用本机IP
西刺获取成功，共有38个IP
开始验证对爬取网站https://www.ximalaya.com/的有效性,时间较长，请等待...
[---------------ip 列表（已省略）-------------]
IP适用，已保存
IP适用，已保存
IP适用，已保存
已删去请求失败IP
IP适用，已保存
---------检测日志（已省略）--------------------
已删去请求失败IP
已删去请求失败IP
IP适用，已保存
已删去请求失败IP
测试完成，适用IP已添加到proxies
proxies已有ip为26个。
代理获取完毕，最终获取到26个可用代理,已写入本地。
```

