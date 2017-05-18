# -*- coding: utf-8 -*-
from .get_mysql_content import especial_using
from .tf_idf import TfIDf
from .k_means import KMeans as K_Means
from sklearn.cluster import KMeans
from sklearn.feature_selection import VarianceThreshold
from sklearn import metrics
from .build_vsm import BuildVsm
from .config import load_data_set, classify_file, classify_file1
import numpy
import time


def cluster(end_time, days, database_name):
    input_time = end_time
    input_day = days
    database_name = database_name
    rows, all_time, all_comment, all_follow = especial_using(input_time, int(input_day), database_name)
    from .config import get_content
    # rows, all_comment, all_follow, all_time = get_content('/home/guoweikuang/weibo_showing/分类结果', '学校新闻.txt')
    print(input_time, input_day)
    print(len(rows))
    start = time.time()
    # 使用TF-IDF算法为每条文本生成tf-idf值，应用于k-means聚类
    tf = TfIDf(rows, all_comment, all_follow, all_time)
    tf_idf_dict = tf.tf_idf()
    # print(sorted(tf_idf_dict.items(), key=lambda d: d[1], reverse=True))
    print('cost: {}'.format(time.time() - start))
    start = time.time()
    # 构建vsm向量空间模型，将文本进行归一化整理
    vsm_file_name = '总聚类结果'
    vsm = BuildVsm(rows, tf_idf_dict)
    scores = vsm.build_vsm(vsm_file_name)
    vsm_file_path = 'vsm集合/{}/{}.txt'.format(vsm_file_name, vsm_file_name)
    print('cost: {}'.format(time.time() - start))
    start = time.time()
    # 使用K_Means算法进行分类步骤如下
    # k_cluster = K_Means(rows, all_comment, all_follow, all_time)
    # data_set = numpy.mat(load_data_set(vsm_file_path))
    # cluster_centroids, cluster_assment = k_cluster.k_means(data_set, 10)
    #
    # # 获取矩阵中所有行的第一列,并生成每条文本所属的标签
    # labels = cluster_assment[:, 0]
    # labels = [int(i[0]) for i in labels.tolist()]
    # classify_file1(labels, '总vsm结果', rows, all_follow, all_comment, all_time)

    # 使用sklearn中的KMeans算法进行聚类
    data_set = numpy.mat(load_data_set(vsm_file_name))
    print('===' * 30)
    vt = VarianceThreshold()
    x_train2 = vt.fit_transform(data_set)
    print('====' * 30)

    cluster = KMeans(init='k-means++', n_clusters=4)
    matrix = cluster.fit_predict(data_set)
    print(metrics.calinski_harabaz_score(data_set, matrix))
    labels = list(matrix)
    classify_file1(labels, '总聚类结果', rows, all_follow, all_comment, all_time, scores, '总聚类结果')
    print('cost: {}'.format(time.time() - start))


if __name__ == '__main__':
    input_time = input('请输入你要抓取的起始日期（2016-11-1）：')
    input_day = input('请输入你要抓取的天数（从起始日期起)：')
    database_name = input('请输入你要获取数据的数据库：')
    # rows, all_time, all_comment, all_follow = especial_using(input_time, int(input_day), database_name)
    from config import get_content
    rows, all_comment, all_follow, all_time = get_content('/home/guoweikuang/weibo_showing/分类结果', '学校新闻.txt')
    print(len(rows))
    start = time.time()
    # 使用TF-IDF算法为每条文本生成tf-idf值，应用于k-means聚类
    tf = TfIDf(rows, all_comment, all_follow, all_time)
    tf_idf_dict = tf.tf_idf()
    print(rows)
    # print(sorted(tf_idf_dict.items(), key=lambda d: d[1], reverse=True))
    print('cost: {}'.format(time.time() - start))
    print(sorted(tf.get_total_keywords().items(), key=lambda d: d[1], reverse=True))
    start = time.time()
    # 构建vsm向量空间模型，将文本进行归一化整理
    vsm_file_name = '总vsm'
    vsm = BuildVsm(rows, tf_idf_dict)
    scores = vsm.build_vsm(vsm_file_name)
    vsm_file_path = 'vsm集合/{}/{}.txt'.format(vsm_file_name, vsm_file_name)
    print('cost: {}'.format(time.time() - start))
    print(scores)
    start = time.time()
    # 使用K_Means算法进行分类步骤如下
    # k_cluster = K_Means(rows, all_comment, all_follow, all_time)
    # data_set = numpy.mat(load_data_set(vsm_file_path))
    # cluster_centroids, cluster_assment = k_cluster.k_means(data_set, 10)
    #
    # # 获取矩阵中所有行的第一列,并生成每条文本所属的标签
    # labels = cluster_assment[:, 0]
    # labels = [int(i[0]) for i in labels.tolist()]
    # classify_file1(labels, '总vsm结果', rows, all_follow, all_comment, all_time)

    # 使用sklearn中的KMeans算法进行聚类
    data_set = numpy.mat(load_data_set(vsm_file_path))
    print('===' * 30)
    vt = VarianceThreshold()
    x_train2 = vt.fit_transform(data_set)
    print(x_train2)
    print(x_train2.shape)
    print(x_train2[:, 1])
    print('====' * 30)

    cluster = KMeans(init='k-means++', n_clusters=4)
    matrix = cluster.fit_predict(data_set)
    print(metrics.calinski_harabaz_score(data_set, matrix))
    print(matrix)
    labels = list(matrix)
    classify_file1(labels, '总vsm结果', rows, all_follow, all_comment, all_time, scores)
    print('cost: {}'.format(time.time() - start))
