# coding=utf-8
import os
import shutil
from .save_to_redis import save_to_redis, remove_to_redis, r
from redis import Redis


r2 = Redis(host="localhost", port=6379, db=1)
abs_filename = os.path.dirname(os.path.abspath(__file__))
print(abs_filename + '/dict/user_stop_word.txt')


def user_stop_word():
    """
    加载停用词
    :return:
    """
    stop_word = []
    with open(abs_filename + '/dict/user_stop_word.txt', 'rb') as f:
        for line in f.readlines():
            stop_word.append(line.decode('utf-8').strip('\n'))
    return stop_word


stop_words = user_stop_word()


def load_data_set(file_name):
    """ 加载数据集文件，没有返回类标号的函数 """
    data_mat = []
    openfile = open(abs_filename + '/vsm集合/' + file_name + '/' + file_name + '.txt')
    print(abs_filename + '/vsm集合/' + file_name + '/' + file_name + '.txt')
    for line in openfile.readlines():
        cur_line = line.strip().split('\t')
        float_line = list(map(float, cur_line))
        # if sum(floatLine) != 0:
        data_mat.append(float_line)
    return data_mat


def load_data_set1(file_name):
    data_mat = []
    openfile = open(abs_filename + '/' + 'vsm集合' + '/' + file_name + '/' + file_name + '.txt')
    for line in openfile.readlines():
        data_mat.append(line)
    return data_mat


def classify_file(labels, filename, rows, follows, comments, times):
    for i in set(labels):
        if r.lrange(filename + str(i + 1), 0, -1):
            remove_to_redis(filename + str(i + 1))

    for i, text, zan, comment, pub_time in zip(labels, rows, follows, comments, times):
        text = text.encode('utf-8')
        zan = '0' if not zan else zan
        comment = '0' if not comment else comment
        zan = zan.encode('utf-8')
        comment = comment.encode('utf-8')
        pub_time = pub_time.encode('utf-8')

        weibo_text = text + '\t'.encode('utf-8') + zan + '\t'.encode('utf-8') \
                                + comment + '\t'.encode('utf-8') + pub_time
        save_to_redis(filename + str(i + 1), weibo_text)


def classify_file1(labels, filename, rows, follows, comments, times, scores, vsm_file_name='vsm集合/总vsm/总vsm.txt'):
    """
    目的：根据聚类后的结果对微博文本进行归类
    :param labels: type->list, 每条微博对应的类别
    :param filename: 保存的文件名
    :param rows: 微博文本
    :param follows: 点赞数
    :param comments: 评论数
    :param times: 评论时间
    :param scores:
    :param vsm_file_name:
    :return:
    """
    file_name = abs_filename + '/总聚类结果/'
    abs_file_name = file_name + filename

    if os.path.exists(abs_file_name):
        shutil.rmtree(abs_file_name, True)
    vsm_lines = load_data_set1(vsm_file_name)
    print(abs_file_name)
    os.makedirs(abs_file_name)
    print(filename)
    for i in set(labels):
        if r.llen(filename + ':cluster:' + str(i + 1)):
            r.delete(filename + ':cluster:' + str(i + 1))
        # if r.get(filename + ':cluster' + str(i + 1)):
        #     r.delete(filename + ':cluster' + str(i + 1))
        # if r.lrange(filename + ':cluster' + str(i + 1), 0, -1):
        #     remove_to_redis(filename + ':cluster' + str(i + 1))

    for i, text, zan, comment, pub_time, line, score in zip(labels, rows, follows, comments, times, vsm_lines, scores):

        zan = '0' if not zan else zan
        comment = '0' if not comment else comment

        text = text.encode('utf-8')
        zan = zan.encode('utf-8')
        comment = comment.encode('utf-8')
        pub_time = pub_time.encode('utf-8')
        name = abs_file_name + "/" + '第%d类.txt' % (i + 1)

        lines = [float(i) for i in line.split()]
        if sum(lines) == 0.0 or max(lines) == sum(lines):
            continue
        with open(name, 'ab') as f:
            f.write(text + '\t'.encode('utf-8') + zan + '\t'.encode('utf-8')
                    + comment + '\t'.encode('utf-8') + pub_time + '\n'.encode('utf-8'))
            f.write(line.encode('utf-8') + '\n'.encode('utf-8'))
            weibo_text = text + '\t'.encode('utf-8') + zan + '\t'.encode('utf-8') \
                         + comment + '\t'.encode('utf-8') + pub_time

            save_to_redis(filename + ':cluster:' + str(i + 1), weibo_text)


def get_content(basedir_name, file_name):
    """
    对file_name类别进行处理，获取内容、点赞数、评论数、时间等，
    为后面的数据集提供数据
    :param basedir_name: 根目录
    :param file_name: 文件名称
    :return: rows, follows,
    """
    rows = []
    follows = []
    comments = []
    times = []
    basedir_name = basedir_name.strip()
    print(basedir_name + '/' + file_name)
    with open(abs_filename + '/' + basedir_name + '/' + file_name, 'rb') as fp:
        for line in fp.readlines():
            text, zan, comment, pub_time = line.decode('utf-8').replace('\n', '').split('\t')
            if len(text) < 10 or int(comment) <= 2:
                continue
            if int(comment) <= 2:
                continue
            rows.append(text)
            follows.append(zan)
            comments.append(comment)
            times.append(pub_time)
    return rows, follows, comments, times


def get_every_content(word, i):
    rows = []
    comments = []
    follows = []
    times = []
    j = r2.lrange(word + ":cluster:" + str(i), 0, -1)
    for text in j:
        content, like, comment, time = text.decode('utf-8').strip().split('\t')
        rows.append(content)
        follows.append(like)
        comments.append(comment)
        times.append(time)
    return rows, comments, follows, times

from redis import Redis

r3 = Redis(host='localhost', port=6379, db=2)

def get_keywords():
    for i in range(1, 10):
        name = '学校新闻:cluster:' + str(i) + ':max'
        if r3.lrange(name, 0, -1):
            key_name = '学校新闻:cluster:' + str(i) + ":keywords"
            keywords = r3.lrange(key_name, 0, -1)
    return keywords


def get_keywords_content():
    for i in range(1, 10):
        name = '学校新闻:cluster:' + str(i) + ':max'
        if r3.lrange(name, 0, -1):
            key_name = '学校新闻:cluster:' + str(i)
            contents = r.lrange(key_name, 0, -1)
    return contents

