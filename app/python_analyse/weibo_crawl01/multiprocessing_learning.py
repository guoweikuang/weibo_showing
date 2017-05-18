# from multiprocessing.dummy import Pool as ThreadPool
# import time
# import requests
#
# url = 'http://httpbin.org/get?a={}'
# headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"}
# def fetch(num):
#     r = requests.get(url.format(num), headers=headers)
#     print('{} cost = {}'.format(num, r.json()['args']['a']))
#     return r.json()['args']['a']
#
# start = time.time()
# result = map(fetch, range(1, 15))
# print(time.time() - start)
#
# start = time.time()
# pool = ThreadPool(processes=8)
# result2 = pool.map(fetch, range(1, 20))
# pool.close()
# pool.join()
# print(time.time() - start)

import time
import requests
import threading
from queue import Queue

url = 'http://httpbin.org/get?a={}'

"""
类WorkManager是一个管理者，管理线程池和任务队列，类Work是具体的一个线程。
给WorkManager分配指定的任务量和线程数，每个线程都从任务队列中获取任务来执行，直到队列中没有任务。
多用在多线程并行抓取任务上。这里的fetch()函数是一个抓取网页代码
"""


class Work(threading.Thread):
    def __init__(self, work_queue, i):
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        self.num = i
        self.start()

    def run(self):
        while True:
            if self.work_queue.empty():
                print("队列是空的，程序退出")
                break
            try:
                func, args = self.work_queue.get()
                func(args)
                self.work_queue.task_done()
            except Exception as e:
                print("程序出错")
                break


class WorkManager(object):
    def __init__(self, work_num=1000, thread_num=4):
        self.work_queue = Queue()
        self.threads = []
        self.url = 'http://httpbin.org/get?a={}'
        self.__init_work_queue(work_num)
        self.__init_thread_pool(thread_num)

    def __init_thread_pool(self, thread_num):
        """ 初始化线程 """
        for i in range(thread_num):
            self.threads.append(Work(self.work_queue, i))

    def __init_work_queue(self, work_num):
        """ 初始化工作队列 """
        for i in range(work_num):
            # url = self.url.format(i)
            self.add_job(fetch, i)

    def add_job(self, func, *arg):
        """ 任务入队 """
        self.work_queue.put((func, *arg))

    def check_queue(self):
        """ 检查剩余队列任务 """
        return self.work_queue.qsize()

    def wait_all_complete(self):
        """ 等待所有线程运行完毕 """
        for item in self.threads:
            if item.isAlive():
                item.join()


headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"}


def fetch(num):
    r = requests.get(url.format(num), headers=headers)
    print('{} cost = {}'.format(num, r.json()['args']['a']))


#     return r.json()['args']['a']

if __name__ == '__main__':
    start = time.time()
    work_manager = WorkManager(30, 12)
    work_manager.wait_all_complete()
    print('剩余队列,', work_manager.check_queue())
    print('花费了，', time.time() - start)
