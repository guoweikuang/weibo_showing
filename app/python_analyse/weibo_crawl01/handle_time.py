# -*- coding: utf-8 -*-
import time
import re


def handle_time(time1):
    # localtime = time.strftime("%Y-%m-%d  %H:%M:%S  ", time.localtime())  # 获取当地时间
    year_time = time.strftime("%Y", time.localtime())
    date_time = time.strftime("%Y-%m-%d ", time.localtime())
    date_time1 = time.strftime("%Y-%m", time.localtime())
    minute = time.strftime("%M", time.localtime())
    hour = time.strftime("%H", time.localtime())
    day = time.strftime("%d", time.localtime())
    hour = int(hour)
    minute = int(minute)
    day = int(day)
    # localtime = str(localtime)
    date_time1 = str(date_time1)
    if '月' in time1:
        time1 = re.sub(r'月', r'-', time1)
        time1 = re.sub(r'日', r'', time1)
        time2 = '{0}-{1}'.format(str(year_time), str(time1))
    elif '今天' in time1:
        time1 = re.sub(r'今天 ', r'', str(time1))
        time2 = str(date_time) + str(time1)
    elif '分钟' in time1:
        pattern1 = re.compile(r'(\d+)')
        time1_num = re.findall(pattern1, time1)
        time1_num = int(time1_num[0])
        if time1_num > minute:
            time1 = time1_num - minute
            time1 = 60 - int(time1)
            if time1 < 10:
                time1 = '0' + str(time1)
            hour -= 1
            if hour < 10:
                hour = '0' + str(hour)
        else:
            time1 = minute - time1_num
            if time1 < 10:
                time1 = '0' + str(time1)
            hour = '0' + str(hour)

        hour = int(hour)
        if hour < 0:
            hour = 24 - hour
            if hour < 10:
                hour = '0' + str(hour)
            day -= 1
        if day < 10:
            day = '0' + str(day)
        time2 = date_time1 + '-' + str(day) + ' ' + str(hour) + ':' + str(time1)
    else:
        time2 = str(time1)
    return time2
