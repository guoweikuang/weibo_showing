# -*- coding: utf-8 -*-
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr


def format_addr(s):
    name, addr = parseaddr(s)
    if __name__ == '__main__':
        return formataddr((Header(name, 'utf-8').encode(), addr))


def send_email(content, comment_number, comment):
    """ 当该微博评论数较多时，通过发邮件提醒有热门话题 """
    from_address = '15602200534@163.com'
    from_password = 'gwk2014081029'
    to_address = '673411814@qq.com'
    smtp_server = 'smtp.163.com'

    text = 'hello, 管理员，广中医I栋有一个热点话题出现了， ' \
           '微博内容是：{0},评论数已经达到{1}了，评论内容如下：{2}'.format(content, comment_number, comment)
    msg = MIMEText(text, 'plain', 'utf-8')
    msg['From'] = format_addr('微博舆情监控系统的通知，来自<%s>' % from_address)
    msg['To'] = format_addr('管理员<%s>' % to_address)
    msg['Subject'] = Header('来自微博舆情监控的通知, 有热点话题出现。。。', 'utf-8').encode()

    server = smtplib.SMTP(smtp_server, 25)
    server.set_debuglevel(1)
    server.login(from_address, from_password)
    server.sendmail(from_address, [to_address], msg.as_string())
    server.quit()
