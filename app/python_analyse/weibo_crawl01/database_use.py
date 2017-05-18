# -*- coding: utf-8 -*-
import pymysql
from DBUtils.PooledDB import PooledDB

pool = PooledDB(pymysql, 5, host='127.0.0.1',
                            user='root',
                            password='2014081029',
                            db='weibo',
                            charset='utf8')
conn = pool.connection()
cur = conn.cursor()


def create_table(table_name):
    try:
        sql1 = "select * from `{}`".format(table_name)
        cur.excute(sql1)
    except:
        try:
            sql = """ CREATE TABLE `%s` (
              `id` int(11) NOT NULL AUTO_INCREMENT,
              `微博内容` text,
              `发布时间` varchar(255) DEFAULT NULL,
              `评论` text,
              `评论个数` varchar(20) DEFAULT NULL,
              `点赞数` varchar(255) DEFAULT NULL,
              `微博内容链接` varchar(255) DEFAULT NULL,
              PRIMARY KEY (`id`)
            ) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4;
            SET FOREIGN_KEY_CHECKS=1;
            """ % table_name
            cur.execute(sql)
        except Exception as e:
            print(e)

def use_mysql_copy(db_name='weibo'):
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='2014081029',
                                 db=db_name,
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection


def use_mysql():
    conn_mysql = pymysql.connect(host='localhost',
                                 user='root',
                                 passwd='2014081029',
                                 db='weibo',
                                 charset='utf8')
    cur = conn_mysql.cursor()
    return conn_mysql, cur


def get_rows(table_name='content'):
    try:
        sql = 'select * from %s;' % table_name
        cur.execute(sql)
        rows = cur.fetchall()
        return rows
    except Exception as e:
        print('原因：', e)
        return None

rows = get_rows()
# conn, cur = use_mysql()
# rows = get_rows()









