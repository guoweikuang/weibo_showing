# -*- coding: utf-8 -*-
import re
import redis
import requests
from redis_service import save_to_redis
from config import (
    PROXY_SITES, PROXY_REGX,
    PROXY_DEST, FETCH_TIMEOUT,
    USER_AGENT_LIST)

session = requests.session()
r = redis.Redis(host='localhost', port=6179, db=0)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'
                  '537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
}


class Fetcher(object):
    """
    代理采集器
    """

    def __init__(self, proxy_dest=PROXY_DEST):
        self.proxy_dest = proxy_dest
        self.fetch_sites = PROXY_SITES
        self.timeout = FETCH_TIMEOUT
        self.user_agent = USER_AGENT_LIST

    def fetch(self):
        """
        采集代理ip
        """
        for url in self.fetch_sites:
            # headers = self.user_agent[random.randint(0, len(self.user_agent))]
            try:
                html = requests.get(url, headers=headers, timeout=self.timeout)
                proxies = re.findall(PROXY_REGX, html.text)

            except requests.exceptions.ConnectTimeout:
                print('[ERROR] fetch {} failed'.format(url))
                proxies = []
            except requests.exceptions.Timeout:
                print('[ERROR] fetch {} failed'.format(url))
                proxies = []
            else:
                print('[OK] {} proxies from {}'.format(len(proxies), url))

            self.output(proxies)

    def output(self, proxies):
        """
        输出代理列表
        proxies: 代理ip列表
        """
        if not proxies:
            return

        with open(self.proxy_dest, 'a') as f:
            for proxy in proxies:
                save_to_redis('proxy_list', proxy)
                f.write('{}\n'.format(proxy))


def main():
    Fetcher().fetch()


if __name__ == '__main__':
    main()
