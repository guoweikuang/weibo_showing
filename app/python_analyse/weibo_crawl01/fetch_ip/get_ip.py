# coding: utf-8
import requests
from urllib import request
from http.cookiejar import CookieJar
from bs4 import BeautifulSoup
from multiprocessing import Pool
# from gevent import monkey
# monkey.patch_all()
# from gevent.pool import Pool as ThreadPool


class FetcherIP(object):
    def __init__(self):
        self.headers = [('User-Agent','Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25'),
                        ('Host','www.xicidaili.com'),
                        ('Referer','http://www.xicidaili.com/n')]
        self.using_ip = []

    def getCookie(self):
        cookie = CookieJar()
        cookie_support = request.HTTPCookieProcessor(cookie)  # cookie处理器
        opener = request.build_opener(cookie_support)
        opener.addheaders = self.headers
        opener.open('http://www.xicidaili.com/')
        return cookie

    def get_proxy(self):
        with open('proxy.txt', 'w') as f:
            data = []
            cookie = self.getCookie()
            for page in range(1, 101):
                if page % 50 == 0:  # 每50页更新下cookie
                    cookie = self.getCookie()

                url = 'http://www.xicidaili.com/nn/%s' % page
                cookie_support = request.HTTPCookieProcessor(cookie)
                opener = request.build_opener(cookie_support)
                request.install_opener(opener)

                req = request.Request(url, headers=dict(self.headers))
                content = request.urlopen(req)
                soup = BeautifulSoup(content, "lxml")
                trs = soup.find('table', id="ip_list").findAll('tr')
                for tr in trs[1:]:
                    tds = tr.findAll('td')
                    ip = tds[1].text.strip()
                    port = tds[2].text.strip()
                    protocol = tds[5].text.strip()
                    f.write('%s://%s:%s\n' % (protocol, ip, port))
                    address = protocol + '://' + ip + ':' + port
                    data.append(address)
        return data

    def check_ip(self, line):
        line = line.decode('utf-8').replace('\r\n', '')[7:]
        url = 'http://1212.ip138.com/ic.asp'
        proxies = {
            'http': line,
        }
        try:
            html = requests.get(url, timeout=3, proxies=proxies)
            if html.status_code == 200:
                print(line)
                with open('ips.txt', 'ab') as f:
                    f.write(line.encode('utf-8') + '\n'.encode('utf-8'))
        except Exception as e:
            print(e)


class Check_Proxy(object):
    def __init__(self):
        self.proxy = FetcherIP()
        self.is_active_ip = []

    def check_ip(self, line):
        print(line)
        line = line[7:]
        url = 'http://1212.ip138.com/ic.asp'
        proxies = {
            'http': line,
        }
        try:
            html = requests.get(url, timeout=3, proxies=proxies)
            if html.status_code == 200:
                print(line)
                self.is_active_ip.append(line.encode('utf-8'))
            else:
                pass
        except Exception as e:
            print(e)

if __name__ == '__main__':
    pool = Pool(12)
    crawl = FetcherIP()
    # is_active = Check_Proxy()
    # proxy = is_active.proxy.get_proxy()
    # print(proxy)
    # pool = ThreadPool(20)
    # pool.map(is_active.check_ip, proxy)
    # print(is_active.is_active_ip)
    with open('proxy.txt', 'rb') as f:
        my_ip = []
        for line in f.readlines()[:50]:
            pool.apply_async(crawl.check_ip, args=(line, ))

        pool.close()
        pool.join()








# headers = {
#     'User-Agent':'Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25',
#     'Host':'www.xicidaili.com',
#     'Referer':'http://www.xicidaili.com/n',
# }
# html = requests.get('http://www.xicidaili.com/', headers=headers)
#
# print(html.cookies)