# -*- coding: utf-8 -*-
import os
import jieba
from .config import stop_words
from itertools import combinations
from .get_mysql_content import especial_using
from .tf_idf import TfIDf
from .set_vsm import keywords_list

abs_path = os.path.abspath(os.path.dirname(__file__))
# 加载自己定义的字典
# jieba.load_userdict(abs_path + '/dict/dict.txt')


class BuildVsm(object):
    def __init__(self, texts, tf_idf_dicts):
        """
        :param texts: list, 数据集合
        :param tf_idf_dicts: dict,
        :param tf_numbers:  dict,

        """
        self.abs_path = os.path.abspath(os.path.dirname(__file__))
        self.rows = texts
        self.tf_idf_dict = tf_idf_dicts
        self.temp_contents = []
        self.total_seg_list = []
        self.tf_dict = {}
        self.tf_number = {}  # 关键字的频数，没有归一化前的数据
        self.score = []

    @staticmethod
    def handle_filename(filename):
        name = filename + '.txt'
        abs_filename =  abs_path + '/vsm集合/%s/' % filename + name
        print(abs_filename)
        if not os.path.exists(abs_path + '/vsm集合/' + filename):
            os.mkdir(abs_path + '/vsm集合/' + filename)
        if os.path.exists(abs_filename):
            os.remove(abs_filename)
        return abs_filename

    def build_vsm(self, filename):
        """
        构建向量化空间模型，一、进行特征提取，目的是减少向量化维度
        二、进行文本相似度比较，两种实现方法。
        :param contents:
        :return:
        """
        _tf_idf_dict = self.tf_idf_dict
        print('总关键字个数: %s' % str(len(_tf_idf_dict)))
        if len(_tf_idf_dict) > 100:
            tf_idf_list = sorted(_tf_idf_dict.items(), key=lambda d: d[1], reverse=True)[:30]
        else:
            tf_idf_list = sorted(_tf_idf_dict.items(), key=lambda d: d[1], reverse=True)[:30]
        # tf_idf_list = sorted(_tf_idf_dict.items(), key=lambda d: d[1], reverse=True)[:56]
        #print(sorted(_tf_idf_dict.items(), key=lambda d: d[1], reverse=True))
        # print(tf_idf_list)
        keyword_list = [word for (word, value) in tf_idf_list]
        # keyword_list = keywords_list
        removed_words = []

        for row in self.rows:
            seg_list = jieba.cut(row, cut_all=False)
            seg_list = [seg for seg in seg_list]
            removed_words.append(list(set(seg_list) - set(stop_words)))

        two_score = []

        abs_filename = self.handle_filename(filename)   # 进行文件处理操作，若存在则删除

        for words in removed_words:
            score = [0.0] * len(keyword_list)
            union_words = list(set(words) & set(keyword_list))
            for word in union_words:
                number = _tf_idf_dict.get(word, 0.0)
                index = keyword_list.index(word)
                # number = 1.0
                score.pop(index)
                score.insert(index, round(number, 3))
                # score.insert(index, number)

            with open(abs_filename, 'ab') as f:
                number = [str(i) for i in score]
                guo = '\t'.join(number)
                f.write(guo.encode('utf-8') + '\n'.encode('utf-8'))
            two_score.append(score)

        return two_score

if __name__ == '__main__':
    input_time = input('请输入你要抓取的起始日期（2016-11-1）：')
    input_day = input('请输入你要抓取的天数（从起始日期起)：')
    database_name = input('请输入你要获取数据的数据库：')
    rows, all_time, all_comment, all_zan = especial_using(input_time, int(input_day), database_name)
    tf = TfIDf(rows, all_comment, all_zan, all_time)
    tf_idf_dict = tf.tf_idf()

    vsm_file_name = '总vsm'
    vsm = BuildVsm(rows, tf_idf_dict)
    vsm.build_vsm(vsm_file_name)

    vsm_file_path = "{}/{}".format(vsm_file_name, vsm_file_name)

    # from set_vsm import *
    # from collections import OrderedDict
    # from collections import defaultdict
    # result = defaultdict(list)
    # keywords_dict = OrderedDict()
    # total = []
    # for words in cluster_len:
    #     keywords = []
    #     for word in words:
    #         if word in tf_idf_dict:
    #             keywords.append(tf_idf_dict.get(word))
    #             keywords_dict[word] = tf_idf_dict.get(word)
    #         else:
    #             keywords.append(0.0)
    #             keywords_dict[word] = 0.0
    #     total.append(keywords)
    # print(total)
    # print(len(keywords_dict))
    # words_len = len(keywords_dict)
    # print(keywords_dict)
    # values = [value for (name, value) in keywords_dict.items()]
    # names = [name for (name, value) in keywords_dict.items()]
    # print(values)
    # print(keywords_list)
    # print(len(values) == len(keywords_list))
    # total_cent = []
    # for index, words in enumerate(cluster_len):
    #     cent = [0.0] * len(names)
    #     for word in words:
    #         index = names.index(word)
    #         cent.pop(index)
    #         cent.insert(index, values[index])
    #     total_cent.append(cent)
    # print(total_cent)
    # print(len(names))
    # print('==' * 40)
    # for ct in total_cent:
    #     print(ct)


    # result[0].append(total[:len(cluster_cent1)])
    # result[1].append(total[len(cluster_cent1): len(cluster_cent2)])





