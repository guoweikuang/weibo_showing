# -*- coding: utf-8 -*-
import math
from itertools import combinations


def get_distance(two_vector, content):
    """
    实现文本相似度比较算法
    :param two_vector: 两组需要进行比较的文本向量化的列表
    :return:
    """
    total_number = sum([i * j for i, j in zip(two_vector[0], two_vector[1])])
    number1 = math.sqrt(sum([i ** 2 for i in two_vector[0]]))
    number2 = math.sqrt(sum([i ** 2 for i in two_vector[1]]))
    if number1 * number2 == 0:
        result = 0.0
    else:
        result = total_number / number1 * number2
    # print('余弦相似度算法 :  {}'.format(result))
    return result


def similarity_two_text(weights, contents):
    print(contents[:100])
    two_content = combinations(weights[:200], 2)
    text = combinations(contents[:200], 2)
    all_results = []
    all_contents = []
    for words, content in zip(two_content, text):
        # print(content)
        # number = cosine_similarity(words[0], words[1])
        # result = nltk.cluster.cosine_distance(words[0], words[1])
        # print('nltk相似度算法 :  {}'.format(number))
        result = get_distance(words, content)
        all_results.append(result)
        all_contents.append(content)

    top = sorted(all_results, reverse=True)[:10]
    top_contents = [all_results.index(text) for text in top]
    top_contents = [all_contents[index] for index in top_contents]
    top_result = set()
    for i, j in zip(top_contents, top):
        for text in i:
            top_result.add(text)
        print(i)
        print(j)
    print(top_result)