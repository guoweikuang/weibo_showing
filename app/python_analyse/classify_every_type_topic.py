#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import numpy
from .tf_idf import TfIDf
from .build_vsm import BuildVsm
from sklearn.cluster import KMeans
from .save_to_redis import r, remove_to_redis
from .save_to_redis import save_to_redis, remove_to_redis
from .config import load_data_set, classify_file1, abs_filename, get_content, get_every_content
from .get_hot_topic import HotClassify


basedir_name = os.path.dirname(os.path.abspath(__file__))
print(basedir_name)

def handle_topic_redis(file):
    """
    对该类型聚类结果，热度等进行判断，如存在则删除
    :param file: 类型名称
    :return: None
    """
    word = [u':hot', u':keyword', u':max', u':聚类结果']
    for name in word:
        file_name = file + name
        if r.lrange(file_name, 0, -1):
            remove_to_redis(file_name)


def k_means_every_type_topic():
    basedir_name = os.path.dirname(os.path.abspath(__file__))
    file_list = os.listdir(basedir_name + '/分类结果')
    basedir_name = u'分类结果'
    print(file_list)
    for file_name in file_list:
        print('聚类类别，{}'.format(file_name[:-4]))
        handle_topic_redis(file_name[:-4])
        print(file_name)
        rows, comments, follows, times = get_content(basedir_name, file_name)

        tf = TfIDf(rows, comments, follows, times)
        tf_idf_dict = tf.tf_idf()
        print(len(rows))
        print(sorted(tf_idf_dict.items(), key=lambda d: d[1], reverse=True)[:20])
        vsm = BuildVsm(rows, tf_idf_dict)
        scores = vsm.build_vsm(file_name[:-4])

        vsm_abs_path = 'vsm集合/{}/{}.txt'.format(file_name[:-4], file_name[:-4])

        if len(rows) >= 120:
            n = 5
        elif len(rows) >= 50:
            n = 4
        elif len(rows) <= 30:
            n = 2
        else:
            n = 3

        k_cluster = KMeans(init='k-means++', n_clusters=n)
        data_set = numpy.mat(load_data_set(file_name[:-4]))
        print(len(data_set))
        labels = k_cluster.fit_predict(data_set)
        labels = list(labels)
        classify_file1(labels, file_name[:-4], rows, follows, comments, times, scores, file_name[:-4])
        get_every_type_top_keyword()

from redis import Redis
r2 = Redis(host='localhost', port=6379, db=2)
r3 = Redis(host='localhost', port=6379, db=2)

def get_every_type_top_keyword():
    word_tag = ['买卖交易', '求助', '校园生活', '学校新闻', '网络', '情感', '毕业话题']
    keywords = {}
    print('生成')
    hot = HotClassify()
    for word in word_tag:
        print(word)
        hot.cal_cluster_hot(word)
    for word in word_tag:
        for i in range(1, 10):
            if r2.lrange(word + ":cluster:" + str(i) + ":keywords", 0, -1):
                r2.delete(word + ":cluster:" + str(i) + ":keywords")
            if r2.lrange(word + ":cluster:" + str(i) + ":values", 0, -1):
                r2.delete(word + ":cluster:" + str(i) + ":values")
            if r2.lrange(word + ":cluster:" + str(i) + ':max', 0, -1):
                rows, comments, follows, times = get_every_content(word, i)
                tf = TfIDf(rows, comments, follows, times)
                tf_idf_dict = tf.tf_idf()
                tf_idf_dict = sorted(tf_idf_dict.items(), key=lambda d: d[1], reverse=True)
                keywords[word + ":cluster:" + str(i)] = tf_idf_dict[:10]
                
                for t in tf_idf_dict[:10]:
                    print(t)
                    r2.lpush(word + ":cluster:" + str(i) + ":keywords", t[0])
                    r2.lpush(word + ":cluster:" + str(i) + ":values", t[1])      
                

if __name__ == '__main__':
    k_means_every_type_topic()
