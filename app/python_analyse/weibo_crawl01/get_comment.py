# -*- coding: utf-8 -*-
from .get_page import *
from bs4 import BeautifulSoup
import re



# 获取一页微博中的所有评论大于0的评论并返回列表
def get_comment_url(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    comment_total_url_lists = []
    comment_nums = 0
    for comment_url in soup.find_all('a', class_="cc"):
        num = re.split(r'\[(.*?)\]', comment_url.get_text())[1]
        num = int(num)
        if num != 0:
            comment_total_url_lists.append(comment_url.get('href'))
            comment_nums += 1
    print('评论链接不为零个数：{:d}'.format(comment_nums))
    return comment_total_url_lists


# 获取一个页面的所有微博内容的所有评论个数并加入列表中
def get_comment_num(html_content):
    num_comment = []
    num_zan = []
    soup = BeautifulSoup(html_content, 'lxml')
    for attitude in soup.find_all('div', class_="c", id=True):

        zan = attitude.find_all('a')

        total = zan[::-1]
        handle_zan = str(total[3])

        comment_num = str(total[1])
        comment_num = re.findall(r'\[(\d+)\]', comment_num)
        comment_num = int(comment_num[0])

        if comment_num != 0:
            num_comment.append(comment_num)
            num_attitude = re.findall(r'\[(\d+)\]', handle_zan)
            if num_attitude:
                num_zan.append(int(num_attitude[0]))
            else:
                pass
    assert len(num_comment) == len(num_zan)
    return num_comment, num_zan


if __name__ == '__main__':
    comment_url_list = []
    start = input('输入要抓取的页面:')
    html = get_start_page('http://weibo.cn/gzyhl', int(start))
    # comment_url_list = get_comment_url(html)
    number = get_comment_num(html)
    print(number)
