# -*- coding: utf-8 -*-
import re
import time
import random
import requests
import threading
from pool import Pool
from config import (
    PROXY_DEST, PROXY_GOOD_DEST, TEST_TIMEOUT,
    TEST_URL, CHECK_MARK, USER_AGENT_LIST, REFERER_LIST,
    POOL_SIZE
)

# proxy compile
REGX = r"(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3}):(\d{1,5})"
PROXY_RE = re.compile(REGX)

GOOD_STATUS = 1
BAD_STATUS = 0


class Tester(object):
    """ 代理测试器 """

    def __init__(self,
                 input_file=PROXY_DEST,
                 out_file=PROXY_GOOD_DEST,
                 timeout=TEST_TIMEOUT,
                 test_url=TEST_URL,
                 cherk_mark=CHECK_MARK):
        self.input_file = input_file
        self.out_file = out_file
        self.timeout = timeout
        self.test_url = test_url
        self.cherk_mark = cherk_mark

        self.good_proxies = set()
        self.bad_proxies = set()
        self.all_proxies = self.load_proxies(self.input_file)
        self.lock = threading.Lock()

    def load_proxies(self, filename):
        """ 加载filename的代理ip """
        proxy_list = set()
        with open(filename, 'rb') as f:
            for line in f:
                proxy = line.strip().decode('utf-8')
                if not self.check_proxy(proxy):
                    continue
                proxy_list.add(proxy)
        return proxy_list

    @staticmethod
    def check_proxy(proxy):
        """ 验证代理ip是否合法 """
        m = PROXY_RE.match(proxy)
        items = m.groups()
        try:
            if not int(items[4]) < 65536:
                return False
            for i in range(4):
                if not 0 < int(items[i]) < 255:
                    return False
        except (ValueError, IndexError):
            return False
        return True

    def do_test(self, proxy):
        proxies = {
            'http': proxy
        }
        headers = {
            'User-Agent': random.choice(USER_AGENT_LIST),
            'Referer': random.choice(REFERER_LIST)
        }
        start_time = time.time()
        try:
            html = requests.get(self.test_url, timeout=self.timeout,
                                headers=headers, proxies=proxies)
            status_code = html.status_code
            content = html.text
        except:
            self.bad_proxies.add(proxy)
            self.log(BAD_STATUS, proxy, time.time() - start_time)
            return
        end_time = time.time() - start_time
        if self.content_test(status_code, content):
            self.good_proxies.add(proxy)
            self.log(GOOD_STATUS, proxy, end_time)
            self.good_output(proxy, end_time)
        else:
            self.bad_proxies.add(proxy)
            self.log(BAD_STATUS, proxy, end_time)

    def content_test(self, status_code, content):
        """
        status_code: 状态码
        content: 对应正文
        """
        if status_code != 200:
            return False
        if self.cherk_mark not in content:
            return False
        return True

    def log(self, status, proxy, speed):
        """
        status: int, 1:good, 0: bad
        proxy: str, 代理ip
        speed: float, 速度
        """
        with self.lock:
            msg = "%s [%d,%d,%d] %s time: %f" % \
                  ("[OK]" if status else "[ERROR]",
                   len(self.good_proxies), len(self.bad_proxies),
                   len(self.all_proxies), proxy, speed)
            print(msg)

    def good_output(self, proxy, speed):
        with self.lock:
            with open(self.out_file, 'a') as f:
                f.write("%s|%s\n" % (proxy, speed))


def main():
    tester = Tester()
    pool = Pool(size=POOL_SIZE)
    pool.add_tasks(
        [(tester.do_test, (proxy,)) for proxy in tester.all_proxies])
    pool.run()


if __name__ == '__main__':
    main()
