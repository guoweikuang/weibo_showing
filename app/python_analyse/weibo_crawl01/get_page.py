# -*- coding: utf-8 -*-
import requests
import os
from bs4 import BeautifulSoup
import time
from http.cookiejar import LWPCookieJar
import random

session = requests.Session()

# 使用headers来模拟浏览器的行为
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Connection': 'keep-alive',
}
abs_path = os.path.abspath(os.path.dirname(__file__))


def get_cookie_path():
    """ 随机获取cookie """
    path_from_cookies = abs_path + r'/cookies'
    cookies = []
    for file in os.listdir(path_from_cookies):
        cookies.append(file)
    return random.choice(cookies)


cookie_path = abs_path + r'/cookies/' + get_cookie_path()
load_cookiejar = LWPCookieJar()
load_cookiejar.load(cookie_path, ignore_discard=True, ignore_expires=True)
load_cookies = requests.utils.dict_from_cookiejar(load_cookiejar)
cookie = requests.utils.cookiejar_from_dict(load_cookies)


def get_random_cookie():
    random_cookie_path = abs_path + r'/cookies/' + get_cookie_path()
    load_cookiejar_random = LWPCookieJar()
    load_cookiejar_random.load(random_cookie_path, ignore_discard=True, ignore_expires=True)
    load_random_cookies = requests.utils.dict_from_cookiejar(load_cookiejar_random)
    random_cookie = requests.utils.cookiejar_from_dict(load_random_cookies)
    return random_cookie, random_cookie_path


def get_proxy():
    """ 从txt文本读取可用ip
    """
    proxy_file = abs_path + r'/proxy_fetcher/good_proxy_list.txt'
    ip_lists = []
    with open(proxy_file, 'rb') as f:
        for line in f.readlines():
            ip_lists.append(line.decode('utf-8').strip('\r\n'))
    return ip_lists


ip_list = get_proxy()


def get_one_proxy():
    ip = random.choice(ip_list).split('|')[0].encode('utf-8')
    proxies = {
        'http': 'http://' + ip.decode('utf-8')
    }
    return proxies


def get_start_page(start_url, page):
    """ 用cookie模拟登录微博手机版,获取微博内容并返回页面的内容 """
    # time.sleep(0.5)
    url = start_url + '?page={}&vt=4'.format(page)
    _cookie, _cookie_path = get_random_cookie()
    try:
        _html = requests.get(url, cookies=_cookie, timeout=6, headers=headers)
        if _html.status_code == 200:
            return _html.text
        elif _html.text is None:
            print(_cookie)
            get_start_page(start_url, page)
        else:
            print(_cookie_path)
            get_start_page(start_url, page)
    except requests.exceptions.ConnectTimeout:
        print("timeout")
        get_start_page(start_url, page)
    except requests.exceptions.Timeout:
        print('timeout')
        get_start_page(start_url, page)
    except Exception as e:
        print('原因：{}'.format(e))
        get_start_page(start_url, page)


# 调用BeautifulSoup获取微博页面内容
def soup_get_page(texts):
    """
        注意这里的编码问题，一开始html的内容是bytes类型，所以需要用decode
        从指定编码方式解码为unicode方式
    """
    soup = BeautifulSoup(texts, 'lxml')
    for content in soup.find_all('span', class_="ctt")[2:]:
        print(content.get_text())
    print('==' * 40)


if __name__ == '__main__':
    # url = 'http://weibo.cn/comment/E7nbz6nOw?uid=1844617613&rl=0&vt=4#cmtfrm'
    # html = session.get(url, cookies=cookie, headers=headers).content.decode('utf-8')
    # print(html)
    # input_num = input('请输入要抓取的页面:')
    # login()
    # html = requests.get('http://www.baidu.com').content
    # print(html.decode('utf-8'))
    for i in range(1, 10):
        html = get_start_page('http://weibo.cn/gzyhl', i)
