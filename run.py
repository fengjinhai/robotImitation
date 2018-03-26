#!/usr/bin/env python
# encoding: utf-8
import re
import random
import sys
import time
from weibo import Weibo
from push import Push
sys.path.append('../conf')
from commentText import commentText
from userInfo import userInfo  

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
    url = 'http://weibo.com/u/5898432231?refer_flag=0000015010_&from=feed&loc=nickname'
    global weibo
    weibo = login(username, passwd)
    push = Push(weibo)
    text = random.sample(commentText, 1)[0]
    #push.publish()
    #push.like_publish()
    #push.like_comment()
    time.sleep(10)
    #访问被评论人的主页
    personalUrl = re.findall(r".*weibo\.com\/\d{0,20}", url)[0]
    ret = push.visit(personalUrl)
    if not ret:
        print 'visit be act personal page error'
        return False
    else:
        sleepSeconds = random.randint(60, 120)
        print 'visit be act peronal page success, waiting for %d seconds'%sleepSeconds
        time.sleep(sleepSeconds)
    #点击到评论页面
    url = "http://weibo.com/5876579840/EFQRIBdmC?from=page_1006065876579840_profile&wvr=6&mod=weibotime&type=comment#_rnd1493179391288"
    text = '读书的时候很文静'
    ret = push.comment(url, url, text)
    if not ret:
        print 'comment error'
        return False
    else:
        sleepSeconds = random.randint(60, 120)
        time.sleep(sleepSeconds)
        print 'comment success, waiting for %d seconds exit'%sleepSeconds

if __name__ == "__main__":
    userInfo = {'username': 'zezhi7751@sina.cn', 'passwd':'hai456123'}
    username = userInfo['username']
    passwd = userInfo['passwd']
    main(username, passwd)
