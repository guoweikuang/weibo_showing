# -*- coding: utf-8 -*-
"""
线程池，高效执行任务
"""

from queue import Queue
import threading


class Task(threading.Thread):
    """ 任务类 """

    def __init__(self, num, input_queue, out_queue, error_queue):
        super(Task, self).__init__()
        self.thread_name = 'thread %s' % num
        self.input_queue = input_queue
        self.out_queue = out_queue
        self.error_queue = error_queue
        self.daemon = True
        self.lock = threading.Lock()

    def run(self):
        while True:
            try:
                func, args = self.input_queue.get(block=False)
            except Queue.Empty:
                print('%s finished!' % self.thread_name)
                break
            try:
                result = func(*args)
            except Exception as e:
                self.error_queue.put((func.func_name, args, str(e)))
            else:
                self.out_queue.put(result)


class Pool(object):
    """ 线程池 """

    def __init__(self, size):
        self.input_queue = Queue()
        self.out_queue = Queue()
        self.error_queue = Queue()
        self.tasks = [
            Task(num, self.input_queue, self.out_queue,
                 self.error_queue) for num in range(size)
            ]

    def add_task(self, func, args):
        """ 添加单个任务 """
        if not isinstance(args, tuple):
            raise TypeError('args must be tuple type!')
        self.input_queue.put((func, args))

    def add_tasks(self, tasks):
        """ 批量添加任务 """
        if not isinstance(tasks, list):
            raise TypeError('args must be tuple type!')
        for func, args in tasks:
            self.add_task(func, args)

    def get_results(self):
        while not self.out_queue.empty():
            print('results ', self.out_queue.get())

    def get_errors(self):
        """获取执行失败的结果集
        """
        while not self.error_queue.empty():
            func, args, error_info = self.error_queue.get()
            print("Error: func: %s, args : %s, error_info : %s"
                  % (func.func_name, args, error_info))

    def run(self):
        for task in self.tasks:
            task.start()
        for task in self.tasks:
            task.join()


def test(i):
    """test """
    result = i * 10
    return result


def main():
    pool = Pool(size=5)
    pool.add_tasks([(test, (i,)) for i in range(100)])
    pool.run()


if __name__ == '__main__':
    main()
