# -*- coding: utf-8 -*-
import requests
import re
from PIL import Image
from http.cookiejar import LWPCookieJar
import os

session = requests.session()
headers = {
    "User-Agent": '"Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0"',
    "Host": 'login.weibo.cn',
    "Origin": 'https://login.weibo.cn',
    "Referer": "https://login.weibo.cn/login/"
}

url_login = 'https://login.weibo.cn/login/'


def before_login(before_login_url):
    html = session.get(before_login_url, headers=headers).text

    pattern = r'action="(.*?)".*?type="password" name="(.*?)".*?name="vk" value="(.*?)".*?name="capId" value="(.*?)"'
    message_list = re.findall(pattern, html, re.S)
    print(message_list)
    return message_list


def get_cha(cap_id):
    cha_url = "http://weibo.cn/interface/f/ttt/captcha/show.php?cpt="
    cha_url = cha_url + cap_id
    print(cha_url)
    cha = session.get(cha_url, headers=headers)
    with open('cha.jpg', 'wb') as f:
        f.write(cha.content)
        f.close()
    try:
        im = Image.open('cha.jpg')
        im.show()
        im.close()
    except:
        print("请到当前目下去找cha.jpg 输入验证码")
    cha_code = input("请输入验证码:")

    return cha_code


def login():
    global username, my_password
    totals = {
        # 'xhdrzcyq@mailnesia.com': 'z3vgwakvy',
        # 'qkgvpggrn@mailnesia.com': 'pvyqhkzvg',
        # 'wsqauhtpd@mailnesia.com': 'b3vzc7cq',
        # 'xsfwthgc@mailnesia.com': 'vba9tq37',
        #  'qyeuvvvd@mailnesia.com': 'vzd2thpmwx5',
        # 'prwwqsddg@mailnesia.com': 'zuaavgy4qg9'
        #'18902304731': 'gwk2014081029'
        '15602200534': 'guoweikuang2016'
    }
    # username = '15602200534'
    # my_password = 'guoweikuang2015'

    # totals = sorted(totals.items(), key=lambda d:d[1], reverse=True)
    print(totals)
    for (user, passwd) in totals.items():
        # username = user
        # my_password = passwd

        filenames = os.listdir('/home/guoweikuang/weibo_showing/app/python_analyse/weibo_crawl01/cookies')
        name = user[:4] + '.txt'
        if name in filenames:
            continue
        else:
            username = user
            my_password = passwd
    # username = input('请输入你要模拟登录的微博账号名：')
    # my_password = input('请输入你的密码：')
    # username = '18902304731'
    # my_password = 'gwk2014081029'

    message = before_login(url_login)
    post_url, password, vk, cap_id = message[0]
    captcha = get_cha(cap_id)
    login_url = 'https://login.weibo.cn/login/'
    postdata = {"mobile": username, "code": captcha, 'remember': "on", "backURL": "http%3A%2F%2Fweibo.cn",
                "backTitle": "手机新浪网", "tryCount": "", "vk": vk, "capId": cap_id,
                "submit": "登录", password: my_password}
    post_url = login_url + post_url
    html = session.post(post_url, data=postdata, headers=headers)
    print(html.content.decode('utf-8'))
    print(html.cookies.get_dict())
    url = 'http://weibo.cn/gzyhl?page=1'
    html1 = session.get(url)
    print(html1.status_code)
    print(html1.cookies)
    print(session.cookies.get_dict())
    file = 'home/guoweikuang/weibo_showing/app/python_analyse/weibo_crawl01/cookies/'
    file1 = '{}.txt'.format(username[:5])
    file += file1
    file = 'cookie.txt'
    if not os.path.exists(file):
        os.mkdir(file)
    file_cookiejar = LWPCookieJar(file)
    requests.utils.cookiejar_from_dict({c.name: c.value for c in session.cookies}, file_cookiejar)
    file_cookiejar.save(file, ignore_discard=True, ignore_expires=True)
    print(html1.content.decode('utf-8'))

if __name__ == '__main__':
    login()
