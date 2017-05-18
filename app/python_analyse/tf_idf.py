# -*- coding: utf-8 -*-
import os
import math
import jieba
from collections import Counter
from .save_to_redis import save_to_redis
from .config import stop_words

abs_path = os.path.abspath(os.path.dirname(__file__))
# 加载自己定义的字典
jieba.load_userdict(abs_path + '/dict/dict.txt')


class TfIDf(object):
    def __init__(self, rows, all_comment=None, all_zan=None, all_time=None):
        """
        :param rows: list, 数据集合
        :param all_comment: list, 评论集合 -> [2, 2, 5, 7]
        :param all_zan:  list, 点赞集合 -> [1, 5, 0, 3]
        :param all_time: list, 发布时间集合 -> ['2016-10-31 01:37', '2016-11-01 11:13']
        """
        self.abs_path = os.path.abspath(os.path.dirname(__file__))
        self.rows = rows
        self.all_time = all_time
        self.all_comment = all_comment
        self.all_zan = all_zan
        self.temp_contents = []
        self.total_seg_list = []
        self.tf_dict = {}
        self.tf_idf_dict = {}
        self.tf_number = {}    # 关键字的频数，没有归一化前的数据
        self.score = []

    @staticmethod
    def get_seg_content(rows, all_comment):
        # 加载自己定义的字典
        # jieba.load_userdict(abs_path + '\\dict\\dict.txt')
        temp_seglist = []  # 去除停用词后的分词集合
        weibo = []
        jieba.suggest_freq('想问', True)
        for row, comment in zip(rows, all_comment):

            weibo.append(row)
            seg_list = jieba.cut(row, cut_all=False)
            # seg_content = ' '.join(list(seg_list))
            seg_content = list(seg_list)
            content = set(seg_content) - set(stop_words)
            content = [word.strip('\u200b') for word in content]
            if len(content) > 10:
                temp_seglist.append(' '.join(content))   # 集合差，去除停用词
        # print(temp_seglist)
        # print(weibo)
        return temp_seglist

    def get_total_keywords(self):
        """
        统计分词去除停用词和长度小于2后的关键词数量
        contents: 数据源，即所有的文本
        return: 返回统计后所有关键字的字典
        例如： count = {'广中医': 23, '一商': 21}
        """
        temp_seg_list = self.get_seg_content(self.rows, self.all_comment)
        total = ' '.join(temp_seg_list)
        # 把所有关键字集合在一起，再统计每个关键词出现次数
        self.total_seg_list = [word for word in total.split()]

        # 使用collections库来统计关键字个数
        count = Counter()
        for seg in self.total_seg_list:
            count[seg] = count.get(seg, 0) + 1
        # print(sorted(count.items(), key=lambda d: d[1], reverse=True)[:50])
        return count

    def get_tf(self):
        """
        计算所有关键字的tf值
        return： 所有关键字的tf字典
        例: self.tf_dict = {'广中医': 0.023, '一商': 0.007}
        """
        self.tf_number = self.get_total_keywords()

        count = self.get_total_keywords()
        max_number = len(count)

        for name, value in count.items():
            if value >= 1:
                self.tf_dict[name] = float(value / max_number)

    def tf_idf(self):
        """
        计算所有关键字的tf-idf权重
        :return: 所有关键字的tf-idf权重字典
        """
        self.get_tf()
        for name, value in self.tf_dict.items():
            self.tf_idf_dict[name] = float(value * float(math.log(len(self.tf_dict) / (value + 1))))
        return self.tf_idf_dict

