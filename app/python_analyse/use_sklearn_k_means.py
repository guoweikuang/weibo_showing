# -*- coding: utf-8 -*-
from sklearn.cluster import KMeans
import pymysql
import pymysql.cursors

connection = pymysql.connect(host='localhost',
                             user='root',
                             password='gwk2014081029',
                             db='test',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)

try:
    with connection.cursor() as cursor:
        sql = "INSERT users(email, password) VALUES (%s, %s)"
        cursor.execute(sql, ('guoweikuang', 'gwk2014081029'))

    connection.commit()

finally:
    connection.close()