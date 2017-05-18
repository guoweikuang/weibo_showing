# -*- coding: utf-8 -*-
# from classify_every_type_topic import k_means_every_type_topic
# from classify_topic import Classify
from ..python_analyse.weibo_crawl01.main import main
from multiprocessing import Pool, freeze_support, Process
import time
from celery import Celery


app = Celery('classify_main', backend='redis://localhost/5', broker='redis://localhost/0')

def classify_main(start_url, end_time, days):
    """
    页面入口函数：
    :param start_url:
    :param end_time:
    :param days:
    :return:
    """
    print('开始')
    p = Pool(8)
    for i in range(1, int(days)):
        if i % 60 == 0:
            time.sleep(60)
        # main(i, start_url)
        p.apply_async(main, args=(i, start_url))
    # p.close()
    # p.join()

    # p.close()
    # p.join()
    # classify_topic = Classify('分类结果', end_time, days)
    # classify_topic.classify_to_file()
    # k_means_every_type_topic()

import threading


class WorkerThread(threading.Thread):
    def __init__(self, func, url):
        super(WorkerThread, self).__init__()
        self.func = func
        self.url = url

    def run(self):
        self.func(self.url)

def threads_crawl(start_url, end_time, days):
    threads = [WorkerThread(main, i) for i in range(1, int(days))]
    for thread in threads:
        thread.start()

    for t in threads:
        t.join()
    

if __name__ == '__main__':
    classify_main('http://weibo.cn/gzyhl', '2017-03-26', 4)
    # threads_crawl()
