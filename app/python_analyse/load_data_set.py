# -*- coding: utf-8 -*-


def load_data_set(file_name):
    """ 加载数据集文件，没有返回类标号的函数 """
    data_mat = []
    openfile = open(file_name)
    for line in openfile.readlines():
        cur_line = line.strip().split('\t')
        float_line = list(map(float, cur_line))
        # if sum(floatLine) != 0:
        data_mat.append(float_line)
    return data_mat
