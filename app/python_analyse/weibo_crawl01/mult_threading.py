# -*- coding: utf -*-
import threading


class WorkerThread(threading.Thread):
    def __init__(self, func, url):
        super(WorkerThread, self).__init__()
        self.func = func
        self.url = url

    def run(self):
        self.func(self.url)




def main():
    threads = [WorkerThread(worker, i) for i in  range(100, 110)]
    for thread in threads:
        thread.start()

    for t in threads:
        t.join()