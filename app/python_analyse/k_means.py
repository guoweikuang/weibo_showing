# -*- coding: utf-8 -*-
from numpy import *
import os
from .save_to_redis import save_to_redis, remove_to_redis, r
from .load_data_set import load_data_set
from .set_vsm import data_set as data_set_cent


class KMeans(object):
    def __init__(self, content, comments, zans, times=None, file_name='聚类结果1'):
        self.filename = "{0}\\{1}".format(os.path.dirname(os.path.abspath(__file__)), file_name)
        self.rows = content
        self.all_time = times
        self.all_comment = comments
        self.all_zan = zans

    @staticmethod
    def rand_cent(data_set, k):
        """
        data_set: 数据源，特征提取后的各文本特征权重集合
        k: 人工设定的聚类算法中心
        """
        n = shape(data_set)[1]  # 计算列数
        centroids = mat(zeros((k, n)))

        for j in range(n):
            min_j = min(data_set[:, j])  # 找出矩阵data_set每列最小值
            range__j = float(max(data_set[:, j]) - min_j)  # 计算第j列最大值和最小值的差
            # 赋予一个随机质心， 它的值在整个数据集的边界之内
            # random.rand(k,1)构建k行一列，每行代表二维的质心坐标
            centroids[:, j] = min_j + range__j * random.rand(k, 1)
        return centroids  # 返回一个随机的质心矩阵

    @staticmethod
    def set_rand_cent(data_set, k):
        """
        人为设置聚类中心，降低局部最优解出现的概率
        :param data_set:
        :param k:
        :return:
        """
        centroids = mat(data_set_cent)
        return centroids

    def euclidean_distance(vector1, vector2):
        """
        返回两个文本之间的距离
        :param vector1: 文本1的向量列表
        :param vector2:
        :return: 欧式距离
        """
        # return abs(vector1, vector2).max()
        return sqrt(sum(power(vector1 - vector2, 2)))

    def k_means(self, data_set, k, distance=euclidean_distance, create_cent=rand_cent):
        """
        data_set: 数据集
        data_set = [[1.658985, 4.285136], [-3.453687, 3.424321],
                [4.838138, -1.151539],[-5.379713, -3.362104],
                [0.972564, 2.924086]]
        k: 设置聚类簇数K值
        distance：函数, 计算数据点的欧式距离
        例如：vector1 = [[ 1.658985  4.285136]]
          vector2 = [[-3.453687  3.424321]]
        欧氏距离：distance = dist_e(vector1, vector2)
        create_cent: 函数， 返回一个随机的质点矩阵
        """
        m = shape(data_set)[0]  # 获取行数
        cluster_assment = mat(zeros((m, 2)))  # 初始化一个矩阵， 用来记录簇索引和存储误差平方和(指当前点到簇质点的距离）
        centroids = self.rand_cent(data_set, k)  # 随机生成一个质心矩阵蔟
        cluster_changed = True
        print('开始')
        while cluster_changed:
            cluster_changed = False
            for i in range(m):  # 对每个数据点寻找最近的质心
                min_dist = inf  # 设置最小距离为正无穷大
                min_index = -1
                for j in range(k):  # 遍历质心簇，寻找最近质心
                    dist__j = distance(centroids[j, :], data_set[i, :])
                    if dist__j < min_dist:
                        min_dist = dist__j
                        min_index = j
                if cluster_assment[i, 0] != min_index:
                    cluster_changed = True
                cluster_assment[i, :] = min_index, min_dist ** 2  # 平方的意义在于判断聚类结果的好坏

            for cent in range(k):  # 更新质心，将每个簇中的点的均值作为质心
                index_all = cluster_assment[:, 0].A  # 取出样本所属簇的索引值
                value = nonzero(index_all == cent)  # 取出所有属于第cent个簇的索引值
                sample_in_clust = data_set[value[0]]  # 取出属于第I个簇的所有样本点
                centroids[cent, :] = mean(sample_in_clust, axis=0)
        return centroids, cluster_assment


def classify_file(labels, filename, rows, follows, comments, times):
    """
    把数据分类
    :param labels: 聚类出的标签
    :param filename: 数据名称
    :param rows: 数据内容
    :param follows: 点赞数
    :param comments: 评论数
    :param times: 发布时间
    :return:
    """
    for i in set(labels):
        if r.lrange(filename + str(i + 1), 0, -1):
            remove_to_redis(filename + str(i + 1))

    for i, text, zan, comment, pub_time in zip(labels, rows, follows, comments, times):
        zan = '0' if not zan else zan
        comment = '0' if not comment else comment

        text = text.encode('utf-8')
        zan = zan.encode('utf-8')
        comment = comment.encode('utf-8')
        pub_time = pub_time.encode('utf-8')

        weibo_text = text + '\t'.encode('utf-8') + zan + '\t'.encode('utf-8') \
                     + comment + '\t'.encode('utf-8') + pub_time
        save_to_redis(filename + str(i + 1), weibo_text)


def produce_every_type_contents(self, all_max_type_hotpic):
    """
    对聚类结果里的几类文本分别进行汇集，为后面的tf-idf算法实现提供数据源
    :return:
    """
    all_type_list = os.listdir(self.filename)
    max_hoptic = []
    max_top = []
    index = 1
    for every in all_type_list:
        contents = []
        contents_only = []
        every = self.filename + '\\' + every
        with open(every, 'rb') as fp:
            for line in fp.readlines():
                contents.append(line.decode('utf-8').replace('\n', ''))
                content, zan, comment, pub_time = line.decode('utf-8').split('\t')
                contents_only.append(content)
                # contents.append(content)
        self.get_every_tf_idf(contents, contents_only, max_hoptic, self.filename.split('\\')[-1], index)
        index += 1
    print(max_hoptic)
    print(max_top)
    max_name = self.filename.split('\\')[-1]
    # save_to_redis(max_name + 'hot', max_hoptic)
    # save_to_redis(max_name + 'keyword', max_top)
    all_max_type_hotpic[max_name] = max(max_hoptic)
    save_to_redis(max_name + 'max', max(max_hoptic))


def person_distance(self, vector1, vector2):
    """
    : 距离算法
    :param vector1:
    :param vector2:
    :return:
    """
    sum1 = sum(vector1)
    sum2 = sum(vector2)

    sum1_sq = sum([pow(v, 2) for v in vector1])
    sum2_sq = sum([pow(v, 2) for v in vector2])

    p_sum = sum([vector1[i] * vector2[i] for i in range(vector1)])

    num = p_sum - sum1 * sum2 / len(vector1)
    den = sqrt((sum1_sq - pow(sum1, 2) / len(vector1)) * (sum2_sq - pow(sum2, 2)
                                                          / len(vector1)))
    if den == 0:
        return 0

    return 1.0 - num / den


if __name__ == '__main__':
    pass
