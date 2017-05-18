# -*- coding: utf-8 -*-
from config import abs_filename
from tf_idf import TfIDf
from build_vsm import BuildVsm
from k_means import KMeans as K_Means
from sklearn.cluster import KMeans
from config import load_data_set, classify_file1, get_content, abs_filename
import numpy


def get_data_set():
    rows_list = []
    comments_list = []
    follows_list = []
    times_list = []
    second_file_path = abs_filename + '\\总vsm结果\\第12类.txt'
    with open(second_file_path, 'rb') as f:
        for line in f.readlines():
            row, follow, comment, time = line.decode('utf-8').replace('\n', '').split('\t')

            rows_list.append(row)
            follows_list.append(follow)
            comments_list.append(comment)
            times_list.append(time)

    return rows_list, follows_list, comments_list, times_list


def second_cluster_k_means(_rows, _comments, _follows, _times):
    tf = TfIDf(_rows, _comments, _follows, _times)
    tf_idf_dict = tf.tf_idf()
    tf_number = tf.get_total_keywords()
    print(sorted(tf_number.items(), key=lambda d: d[1], reverse=True))
    vsm_file_name = 'second_vsm'
    vsm = BuildVsm(_rows, tf_idf_dict)
    scores = vsm.build_vsm(vsm_file_name)
    vsm_file_path = 'vsm集合\\{}\\{}.txt'.format(vsm_file_name, vsm_file_name)

    k_cluster = K_Means(_rows, _comments, _follows, _times)
    data_set = numpy.mat(load_data_set(vsm_file_path))
    cluster_centroids, cluster_assment = k_cluster.k_means(data_set, 2)

    # # 获取矩阵中所有行的第一列,并生成每条文本所属的标签
    labels = cluster_assment[:, 0]
    labels = [int(i[0]) for i in labels.tolist()]
    classify_file1(labels, 'second_vsm结果', _rows, _follows, _comments, _times, scores)

    # 使用sklearn中的KMeans算法进行聚类
    data_set = numpy.mat(load_data_set(vsm_file_path))
    cluster = KMeans(init='k-means++', n_clusters=2)
    matrix = cluster.fit_predict(data_set)
    print(matrix)
    labels = list(matrix)
    classify_file1(labels, 'second_vsm结果1', rows, follows, comments, times, scores)


if __name__ == '__main__':
    rows, follows, comments, times = get_content(abs_filename+'\\总vsm结果', '第12类.txt')
    second_cluster_k_means(rows, follows, comments, times)