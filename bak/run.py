#!/usr/bin/env python
# encoding: utf-8

from weibo import Weibo
from topic import Topic

import sys

def login(username, passwd):
    '''
    登录
    '''
    weibo = Weibo(username, passwd)
    login = weibo.login()
    if not login[0]:
        try:
            print login[1]
        except:
            print login[1].encode('utf-8')
        sys.exit(1)
    try:
        print 'success login\nuid= %s,'%login[1],'nick=', login[2]
    except:
        print 'success login\nuid= %s,'%login[1],'nick=', login[2].encode('utf-8')
    return weibo


def main(username, passwd):
    '''
    单线程
    '''
    global weibo
    weibo = login(username, passwd)
    '''根据话题爬取话题的所有feeds和评论'''
    tid = '1008081e364a300148a8ca27bd1bba68620f22'
    topic = Topic(weibo, tid)
    topic.getIndex()


if __name__ == "__main__":
    username = "fengjinhaigood@163.com"
    passwd = "fjh@bj"
    main(username, passwd)
