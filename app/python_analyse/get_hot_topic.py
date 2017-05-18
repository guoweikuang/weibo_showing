# -*- coding: utf-8 -*-
#!/usr/bin/env python3
import math
from redis import Redis
from collections import defaultdict
from .save_to_redis import remove_to_redis, save_to_redis


r = Redis(host='localhost', port=6379, db=1)
r1 = Redis(host='localhost', port=6379, db=2)

word_tag = ['买卖交易', '求助', '校园生活', '学校新闻', '网络', '情感', '毕业话题']


class HotClassify(object):
    def __init__(self):
        self.word_tag = word_tag

    def cal_cluster_hot(self, cluster_name):
        """
        计算每一类的热度
        :param name 聚类名称
        """
        hot = {}
        max_hot = {}
        print(cluster_name)
        for i in range(1, 8):
            name = cluster_name + ':cluster:{}'.format(i)
            max_name = cluster_name + ":cluster:{}:max".format(i)
            if r1.lrange(max_name, 0, -1):
                r1.delete(max_name)

            if not r.lrange(name, 0, -1):
                continue      
            contents = r.lrange(name, 0, -1)
            print('zai:{}'.format(contents))
            hot[name] = 0 
            for content in contents:
                text, like, comment, time = content.decode('utf-8').strip().split('\t')
                hot[name] += float(comment) + math.sqrt(float(like))
            max_hot[name] = hot[name]

            r1.lpush(name, hot[name])
            #r1.expire(name, 86400)
            
        max_hot = sorted(max_hot.items(), key=lambda d: d[1], reverse=True)
        print(max_hot)
        r1.lpush(max_hot[0][0] + ':max', max_hot[0][1])


if __name__ == '__main__':
    hot_opt = HotClassify()
    for word in word_tag:
        hot_opt.cal_cluster_hot(word)

            

        


