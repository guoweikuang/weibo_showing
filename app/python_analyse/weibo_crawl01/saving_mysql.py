# -*- coding: utf-8 -*-
import re
from lxml import etree
from .database_use import use_mysql, use_mysql_copy, rows, conn, cur, create_table, get_rows
from .handle_time import handle_time
from .get_page import session, cookie, headers
import time


# 保存数据到数据库
def saving_mysql(table_name, url, total_comment_contents, comment_number, items, comment_times, comment_names, zan_num):
    """
    :param zan_num: 点赞数
    :param url:
    :param total_comment_contents: 一条微博的所有评论内容的字符串
    :param comment_number: 评论个数
    :param items: 加上编号的评论内容的列表
    :param comment_times: 评论时间
    :param comment_names: 评论人昵称
    :return:
    """
    if table_name == 'gzyhl':
        table_name = 'content'
    try: 
        sql = "select * from %s;" % table_name
        cur.execute(sql)
    except:
        print('创建数据库表', table_name)
        create_table(table_name)
    # create_table(table_name)
    comment = session.get(url, cookies=cookie, headers=headers).content
    # 此处使用xpath获取微博内容
    selector = etree.HTML(comment)
    content1 = selector.xpath('//span[@class="ctt"]')[0]
    weibo_content = content1.xpath('string(.)')
    weibo_pattern = re.compile(u'[^\u0000-\uD7FF\uE000-\uFFFF]', re.UNICODE)
    weibo_content = re.sub(weibo_pattern, r'', weibo_content)
    # 获取微博内容的发布时间
    content2 = selector.xpath('//span[@class="ct"]')[0]
    time1 = content2.xpath('string(.)')
    time_pattern = re.compile(u'[^\u0000-\uD7FF\uE000-\uFFFF]', re.UNICODE)
    time1 = re.sub(time_pattern, r'', time1)
    time2 = handle_time(time1)
    # time2 = str(localtime) + str(time1)
    print('验证%s, 评论个数：%d' % (weibo_content, comment_number))
    links = []
    rows = get_rows(table_name)
    for i in rows:
        links.append(i[6])

    if int(comment_number) >= 20:
        link = 'http://weibo.cn/comment/E1xN7ne4F?uid=1844617613&rl=0&vt=4#cmtfrm'
        if url != link:
            pass
            # send_email(weibo_content[1:], comment_number, total_comment_contents)

    if url not in links:
        try:
            # with conn.cursor() as cursor:
            sql = "INSERT INTO %s" % table_name + "(微博内容, 发布时间, 评论, 评论个数, 点赞数, 微博内容链接) " \
                  "VALUES(%s, %s, %s, %s, %s, %s)"
            cur.execute(sql, (weibo_content[1:], time2, str(total_comment_contents),
                                 str(comment_number), str(zan_num), str(url)))
            conn.commit()
        except Exception as e:
            print('失败', e)
            conn.rollback()

        # weibo_id = str(rows[-1][0])

        print(len(items), len(comment_times), len(comment_names))
        #for s, time3, comment_user_name in zip(items, comment_times, comment_names):
        #    try:
        #        # with conn.cursor() as cursor:
        #        sql = "INSERT weibo_commment(id, 评论, 评论时间, 评论链接, 评论用户) " \
        #              "VALUES (%s, %s, %s, %s, %s)"
        #        cur.execute(sql, (weibo_id, str(s), str(time3), str(url), str(comment_user_name)))
        #        conn.commit()

        #    except Exception as e:
        #        print('失败', e)
        #        conn.rollback()
    # cu#r.close()
    # conn.close()
    else:
        for (num, link) in enumerate(rows):
            if url == link[6]:
                try:
                    # with conn.cursor() as cursor:
                    sql2 = "UPDATE %s" % table_name + " SET 评论='%s', 评论个数='%s', 点赞数='%s' WHERE id='%s'" % (
                        str(total_comment_contents), str(comment_number), str(zan_num), str(link[0]))
                    cur.execute(sql2)
                    conn.commit()
                except Exception as e:
                    print('update 失败', e)
                    conn.rollback()

