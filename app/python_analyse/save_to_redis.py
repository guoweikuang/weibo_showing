# -*- coding: utf-8 -*-
from redis import Redis

r = Redis(host='localhost', port=6379, db=1)


def save_to_redis(i, text):
    """
    保存数据到redis的列表数据结构里
    :param i: 数据的标识，即id
    :param text: 数据内容
    :return: None
    """
    r.lpush(i, text)
    r.expire(i, 86400)

def remove_to_redis(name):
    """
    删除redis数据中存在的名称为name列表的数据
    :param name: 数据名称
    :return: None
    """
    number = len(r.lrange(name, 0, -1))
    for i in range(number):
        r.lpop(name)


def show_redis_data(type_name):
    """
    展示数据
    :param type_name:
    :return:
    """
    contents = r.lrange(type_name, 0, -1)
    for content in contents:
        print(content.decode('utf-8'))
