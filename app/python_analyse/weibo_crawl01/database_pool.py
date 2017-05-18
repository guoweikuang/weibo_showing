# -*- coding: utf-8 -*-
from queue import Queue
import threading
import time
import requests
from .database_use import use_mysql_copy

conn = use_mysql_copy('test')
queue = Queue()
queue1 = Queue()

class ThreadPool(object):
    def __init__(self, maxsize):
        self.maxsize = maxsize
        self._q = Queue(maxsize)
        for i in range(maxsize):
            self._q.put(threading.Thread)

    def get_thread(self):
        return self._q.get()

    def add_thread(self):
        self._q.put(threading.Thread)


pool = ThreadPool(8)

def task(arg, p):
    print(arg)
    fetch(arg)
    p.add_thread()

url = 'http://httpbin.org/get?a={}'
headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"}
def fetch(num, conn):
    r = requests.get(url.format(num), headers=headers)
    num = int(r.json()['args']['a'])
    print('{} cost = {}'.format(num, r.json()['args']['a']))
    try:
        with conn.cursor() as cursor:
            sql = "INSERT numbers(number) VALUES(%s)"
            cursor.execute(sql, (num,))
        conn.commit()
    except Exception as e:
        print('原因:', e)


    return r.json()['args']['a']

def produce_pool():
    for i in range(34):
        conn = use_mysql_copy('test')
        conn.autocommit(True)
        queue.put(conn)

def get_task():
    while True:
        conn_copy = queue.get()
        num = queue1.get()
        a = fetch(num, conn_copy)
        queue.task_done()
        queue1.task_done()

def get_content():
    with conn.cursor() as cursor:
        sql = 'select * from numbers;'
        cursor.execute(sql)
        rows = cursor.fetchall()


        print(rows)

import pymysql
def get_content_test():
    conn_mysql = pymysql.connect(host='localhost',
                                 user='root',
                                 passwd='gwk2014081029',
                                 db='weibo',
                                 charset='utf8')
    cur = conn_mysql.cursor()
    sql = 'select * from content;'
    cur.execute(sql)
    rows = cur.fetchall()
    print(rows[:4])
    conn.close()
    cur.close()

if __name__ == '__main__':
    # for i in range(1, 15):
    #     queue1.put(i)
    #
    # for i in range(1, 15):
    #     conn = use_mysql_copy('test')
    #     conn.autocommit(True)
    #     queue.put(conn)
    #
    # for i in range(10):
    #     t = threading.Thread(target=get_task)
    #     t.setDaemon(True)
    #     t.start()
    # queue.join()
    # queue1.join()
    # conn.close()
    conn = use_mysql_copy('test')
    get_content()
    conn.close()
    # get_content_test()
#
# for i in range(34):
#     t = pool.get_thread()
#     obj = t(target=task, args=(i, pool,))
#     obj.start()
