# -*- coding: utf-8 -*-
#!/usr/bin/env python3
import re
import time
import logging
import random
from bs4 import BeautifulSoup
from .get_comment import get_comment_url, get_comment_num
from multiprocessing import Pool
from .database_use import use_mysql, use_mysql_copy, conn, cur
from .get_page import get_start_page, session, cookie, headers
from .saving_mysql import saving_mysql
from .mult_threading import WorkerThread

try: from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass
from threading import Lock
lock = Lock()

def set_logging(file_name='weibo.log', level_name=logging.DEBUG):
    logging.basicConfig(filename=file_name, level=level_name)


# 这个函数的作用是：把一个微博内容的所有评论获取
def comment_content(html, table_name):
    # comment_total = get_comment_num(html)    # 把一页微博内容的评论个数加在一个列表中
    comment_list = get_comment_url(html)     # 把一页微博内容的url加入列表中,前提是加入的微博内容的链接评论个数不为零
    get_need_message(comment_list, html, table_name)


def handle_common_link():
    """
    目的： 获取当月所有的链接来进行判重，这样做的意义是当数据量足够大时，把所有链接放在一个列表里判重，明显内存使用大，
    因此使用当前一个月的链接加入列表这个折中的方法来进行
    """
    sql = 'select * from content;'
    cur.execute(sql)
    rows = cur.fetchall()


# 重构保存在数据库的函数,把所有的步骤合并在这个函数
def get_need_message(comment_url_list, html, table_name):
    """
    :param comment_url_list: 一页内容里的每条微博的评论url
    :param html: 页面内容
    :return: None
    """
    global total_comment_contents1
    print("===================新的函数分界线开始========================")
    comment_total_num, zan_total_num = get_comment_num(html)
    for url, comment_number, zan_num in zip(comment_url_list, comment_total_num, zan_total_num):
        # 设置时间限制,防止爬取评论过快被微博查封ip
        # time.sleep(0.5)
        # 评论每页10条，因此需要计算出页面数，也可以通过标签来确定页数
        if comment_number > 10 and comment_number % 10 > 0:
            page_number = int(comment_number / 10) + 1
        elif comment_number > 10 and comment_number % 10 == 0:
            page_number = int(comment_number / 10)
        else:
            page_number = 1
        y = 1
        comment_times = []
        items = []   # 把所有评论内容加上编号放入一个列表中
        comment_names = []

        for num in range(1, page_number + 1):
            time.sleep(random.randint(1, 2))
            comment_url = url[:-7] + '&' + 'page=%d' % num
            comment_html = session.get(comment_url, cookies=cookie, headers=headers).content
            soup = BeautifulSoup(comment_html, 'lxml')
            index = 0
            index = 1 if num==1 else index
            for content, comment_time, user_name in zip(soup.find_all('span', class_="ctt")[index:],
                                                        soup.find_all('span', class_="ct")[index:],
                                                        soup.find_all(class_="c", id=True)[index:]):
                '''
                    这里使用正则表达式目的是剔除评论中有链接的html标签，关键在于re的sub函数
                    关于正则表达式的使用，请看这里http://cuiqingcai.com/977.html
                '''
                pattern = re.compile(r'<.*?>')
                replace_text = str(content.get_text())
                replace_text = re.sub(pattern, r'', replace_text)
                '''
                    此处使用正则表达式的作用: 微博里面经常有Emoji表情出现,是一种特殊的unicode编码
                    mysql支持的utf8编码最大字符长度为3字节,而emoji表情是4字节编码,因此在存入数据库
                    出现问题,使用表达式去除此编码字符
                '''
                re_pattern = re.compile(u'[^\u0000-\uD7FF\uE000-\uFFFF]', re.UNICODE)
                replace_text = re.sub(re_pattern, r'', replace_text)

                items.append(str(y) + '.' + replace_text)
                # 获取一个微博内容的所有评论的时间并加入列表
                comment_time = comment_time.get_text()
                comment_time = re.sub(r'\'', r'', comment_time)
                localtime_pattern = re.compile(u'[^\u0000-\uD7FF\uE000-\uFFFF]', re.UNICODE)
                comment_time = re.sub(localtime_pattern, r'', str(comment_time))
                current_time = time.strftime("%Y-%m-%d %H:%M:%S  ", time.localtime())
                total_time = str(current_time) + ' ' + str(comment_time)
                comment_times.append(total_time)
                # 获取一条微博的所有评论的用户名并加入列表
                comment_name = user_name.find('a').string
                comment_names.append(comment_name)
                y += 1
                total_comment_contents1 = '     '.join(items)

        total_comment_contents = total_comment_contents1
        saving_mysql(table_name, url, total_comment_contents, comment_number, items, comment_times, comment_names, zan_num)


def main(index, url='http://weibo.cn/gzyhl'):
    print('===================================第%d页=================================' % index)
    html = get_start_page(url, int(index))

    comment_list = get_comment_url(html)
    logging.basicConfig(format='%(asctime)s : %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p',
                        filename='weibo.log', filemode='w', level=logging.DEBUG)
    logging.info(comment_list)

    from urllib.parse import urlparse
    table = urlparse(url)
    table_name = table.path.strip('/')
    comment_content(html, table_name)


def threads_crawl():
    threads = [WorkerThread(main, i) for i in range(6, 15)]
    for thread in threads:
        thread.start()

    for t in threads:
        t.join()
    conn.close()


def only_one_thread(start_url, start_page, days):
    p = Pool(6)

    for i in range(1, int(days) + 1):
        p.apply_async(main, args=(i, start_url))
        # main(i, start_url)
    p.close()
    p.join()
    

if __name__ == '__main__':
    start_url = input('请输入要抓取的网页链接(http://weibo.cn/gzyhl)：')
    select = input('请选择自动获取网页(1)或手动设置获取网页(0):')

    if int(select) not in [x for x in range(0, 2)]:
        print('输入错误，请重新输入:')


    threads_crawl()
    if int(select) == 0:
        page_num = input('输入要抓取的页面上限:')
        page_num1 = input('输入要抓取的页面下限:')
        page_num1 = int(page_num1)
        page_num = int(page_num)
        p = Pool(12)
        # thread_pool()
        # for i in range(page_num1, page_num + 1):
        #     queue.put(i)
        #
        # threads = []
        # for i in range(90, 100):
        #     t = threading.Thread(target=threads_crawl, args=(i, ))
        #     # t.setDaemon(True)
        #     t.start()
        #     threads.append(t)
        # for t in threads:
        #     t.join()
        #
        # queue.join()

        # pool = ThreadPool(processes=8)
        # pool.map(main, range(page_num1, page_num + 1))
        # pool.close()
        # pool.join()
        #
        # for i in range(page_num1, page_num + 1):
        #
        #     queue.put((i, start_url))
        #     conn = use_mysql_copy('weibo')
        #     queue1.put(conn)
        #
        # for i in range(10):
        #     t = threading.Thread(target=threading_fetch)
        #     t.setDaemon(True)
        #     t.start()
        # queue.join()
        # conn = use_mysql_copy('weibo')
        # p.map(main, args=(start_url, [i for i in range(page_num1, page_num + 1)]))

    #     start = time.time()
    #     for i in range(page_num1, page_num + 1):
    #         if i % 60 == 0:
    #             time.sleep(60)
    #         # Process(target=main, args=(start_url, i, lock)).start()
    #         p.apply_async(main, args=(i,start_url))
    #     p.close()
    #     p.join()
    #     print('cost:', time.time() - start)
    # else:
    #     while True:
    #         p = Pool(4)
    #         for i in range(1, 3):
    #             p.apply_async(main, args=(i, start_url))
    #         p.close()
    #         p.join()
    #         time.sleep(3600)
    # connection.close()
    # conn.close()
    conn.close()
