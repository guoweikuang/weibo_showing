# -*- coding: utf-8 -*-
import os
from redis import Redis
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

basedir_name = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
print(basedir_name)

matplotlib.matplotlib_fname()
plt.rcParams['font.sans-serif'] = ['YaHei Consolas Hybrid']
plt.rcParams['axes.unicode_minus'] = False

r = Redis(host="localhost", port=6379, db=2)
word_tag = ['买卖交易', '求助', '校园生活', '学校新闻', '网络', '情感', '毕业话题']
word_tag = [word for word in word_tag]


def get_every_type_max():
    hot = {}
    for word in word_tag:
        temp = []
        for i in range(1, 10):
            if r.lrange(word + ':cluster:' + str(i), 0, -1):
                j = r.lrange(word + ':cluster:' + str(i), 0, -1)[0]
                print(j)
                temp.append(float(j.decode('utf-8')))
        hot[word] = max(temp)
    print(hot)
    return hot


def show_histgoram(hot):
    hot = sorted(hot.items(), key=lambda d: d[1], reverse=True)
    values = [value[1] for value in hot]
    keys = [value[0] for value in hot]
    number = int(len(values))
    ind = np.arange(number)
    hot = tuple(values)
    fig, axes = plt.subplots(1, 1)
    rects = axes.bar(ind, hot, width=0.35, color='rgby', align='center', yerr=0.00000001)
    x_label = tuple(keys)
    axes.set_ylabel(u'最大热度值')
    axes.set_title(u'聚类结果各类别的最大热度值')
    axes.set_xticks(ind)
    axes.set_xticklabels(x_label)
    for rect in rects:
        height = rect.get_height()
        axes.text(rect.get_x() + rect.get_width() / 2, 1.03 * height,
                  '%.2f' % float(height), ha='center', va='bottom')
    plt.savefig(basedir_name + '/static/images/hot.png')
    print('结束')

def show_keyword():
    for word in word_tag:
        for i in range(1, 10):
            if r.lrange(word + ':cluster:' + str(i) + ':max', 0, -1):
                max_name = word + ":cluster:" + str(i) + ':max'
                key_names = r.lrange(word + ':cluster:' + str(i) + ':keywords', 0, -1)
                values = r.lrange(word + ":cluster:" + str(i) + ":values", 0, -1)
                product_keyword(word, key_names, values)

            
def product_keyword(word, key_names, values):
    number = int(len(key_names))
    ind = np.arange(number)
    key_names = [key.decode('utf-8') for key in key_names]
    print(len(key_names))
    values = [float(value) for value in values]
    hot = tuple(values)[::-1]
    print(hot)
    print(ind)
    fig, axes = plt.subplots(1, 1)
    rects = axes.bar(ind, hot, width=0.35, color='rgby', align='center', yerr=0.00000001)
    x_label = tuple(key_names)[::-1]
    axes.set_ylabel(u'关键字权重')
    axes.set_title(u'<{}>类别下热点话题关键字TOP10图'.format(word))
    axes.set_xticks(ind)
    axes.set_xticklabels(x_label)

    for rect in rects:
        height = rect.get_height()
        axes.text(rect.get_x() + rect.get_width() / 2, 1.03 * height,
                 '%.2f' % float(height), ha='center', va='bottom')
    plt.savefig(basedir_name + '/static/images/{}.png'.format(word))

                
if __name__ == '__main__':
    hot = get_every_type_max()
    show_histgoram(hot)
    show_keyword()
