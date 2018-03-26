#!/usr/bin/env python
# encoding: utf-8

import re, json, time, datetime
from bs4 import BeautifulSoup as BS
import random,time
import traceback

def CatchException(func):
    def wrap(*args, **kw):
        try:
            return func(*args, **kw)
        except:
            print 'except',func.__name__
            pass
    return wrap

class Push(object):
    def __init__(self, weibo):
        self.weibo = weibo
        self.comment_url = 'http://weibo.com/aj/v6/comment/add?ajwvr=6&__rnd=%d'%int(round(time.time() * 1000))
        self.publish_url = 'http://weibo.com/aj/mblog/add?ajwvr=6&__rnd=%d'%int(round(time.time() * 1000))
        self.like_publish_url = 'http://weibo.com/aj/v6/like/add?ajwvr=6'
        self.like_comment_url = 'http://weibo.com/aj/v6/like/objectlike?ajwvr=6'
        #self.rid = rid
        self.feeds = []

    def getField(self, htmlBody):
        try:
            uid = re.findall(r"CONFIG\[\'uid\'\]=\'\d{0,20}\'", htmlBody)[0].replace("CONFIG['uid']=","").replace("'","")
            page_id = re.findall(r"CONFIG\[\'page_id\'\]=\'\d{0,30}\'", htmlBody)[0].replace("CONFIG['page_id']=","").replace("'","")
            domain = re.findall(r"CONFIG\[\'domain\'\]=\'\d{0,10}\'", htmlBody)[0].replace("CONFIG['domain']=","").replace("'","")
            location = re.findall(r"CONFIG\[\'location\'\]=\'.{0,30}\'", htmlBody)[0].replace("CONFIG['location']=","").replace("'","")
            #midList = re.findall(r"current_mid=\d{0,30}", htmlBody)
            midList = re.findall(r"rid=\d{15,30}", htmlBody)
            if len(midList) == 0:
                return False 
            mid = midList[0].replace("rid=","").replace("'","")
            fieldDic = {'uid': uid, 'page_id': page_id, 'location': location, 'mid': mid}
        except:
            traceback.print_exc()
            return False
        return fieldDic 

    def makeHeader(self, referer):
        header = {
            'Host': 'weibo.com',
            'Origin': 'http://weibo.com',
            'Pragma': 'no-cache',
            'Referer': referer,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        return header

    def comment(self, url, referer, text=""):
        #访问评论页面
        htmlBody = self.visit(url) 
        sleepSeconds = random.randint(60, 120)
        print 'visit comment page success, waiting for %d seconds'%sleepSeconds
        time.sleep(sleepSeconds)
        fieldDic = self.getField(htmlBody)
        if not fieldDic:
            return False
        postData = {
            'act': 'post',
            'mid': fieldDic['mid'],
            'uid': fieldDic['uid'],
            'forward': '0',
            'isroot': '0',
            'content': text,
            'location': fieldDic['location'],
            'module': 'bcommlist',
            'pdetail': fieldDic['page_id'],
            '_t':0
        }
        header = self.makeHeader(referer)
        jsonData = self.weibo.r.post(self.comment_url, postData, headers = header).text
        data = json.loads(jsonData)
        code = data['code']
        msg = data['msg']
        if code != "100000":
            print 'can not comment reason:%s'%msg
            return False
        newMidList =  re.findall(r"comment_id=\\\"\d{15,30}", jsonData)
        if len(newMidList) == 0:
            print "can get my comment mid"
            return False
        newMid = newMidList[0]
        return newMid 


    def publish(self, referer, text = ""):
        postData = {
            'location': 'v6_content_home',
            'text':'国足加油，期待能够出线',
            'appkey':'',
            'style_type':1,
            'pic_id':'',
            'pdetail':'',
            'rank':'0',
            'rankid':'',
            'module':'stissue',
            'pub_source':'main_',
            'pub_type':'dialog',
            '_t': 0,
        }
        header = self.makeHeader(referer)
        print self.weibo.r.post(self.publish_url, postData, headers = header).text

    def like_publish(self, referer):
        postData = {
             'location': 'v6_content_home',
             'group_source': 'group_all',
             'rid': '1_0_8_2669537541347705214',
             'version': 'mini',
             'qid': 'heart',
             'mid': '4090685231932379',
             'like_src': 1
        }
        header = self.makeHeader(referer)
        print self.weibo.r.post(self.like_comment_url, postData, headers = header).text

    def like_comment(self, referer):
        postData = {
             'location': 'v6_content_home',
             'group_source': 'group_all',
             'rid': '4_0_8_2669537541347705214',
             'object_id': 4090685709235470,
             'object_type' : 'comment'
        }
        header = self.makeHeader(referer)
        print self.weibo.r.post(self.like_comment_url, postData, headers = header).text

    def visit(self, url):
        htmlBody = self.weibo.r.get(url).text
        if len(htmlBody)>10000:
            return htmlBody
        return False


