#!/usr/bin/env python
# encoding: utf-8

import re, json, time, datetime
from bs4 import BeautifulSoup as BS

def CatchException(func):
    def wrap(*args, **kw):
        try:
            return func(*args, **kw)
        except:
            print 'except',func.__name__
            pass
    return wrap

class Topic(object):
    '''
    话题
    '''
    def __init__(self, weibo, tid=""):
        self.weibo = weibo
        self.index_url = 'http://weibo.com/p/' + tid
        self.tid = tid
        self.feeds = []

    def getIndex(self):
        html = self.weibo.r.get(self.index_url)
        contents = self.getHTML(html.text)
        '''
        首页 推荐部分
        '''
        for i in contents:
            data = json.loads(i)
            html =  data.get('html', '')
            self.feeds.extend(self.getFeeds(html))
        '''
        '''
        if not contents:
            return []

        self.action_data = self.getActionData(json.loads(contents[-1])['html'])
        self.nextPage = ""
        self.getMsgList(1) #首页
        '''
        获取剩余的页数微薄
        '''
        self.getRemainPage()
        return self.feeds

    def getRemainPage(self):
        i = 1
        while self.nextPage:
            try:
                html = self.weibo.r.get('http://weibo.com'+self.nextPage)
                contents = self.getHTML(html.text)
                data = json.loads(contents[-1])
                self.action_data = self.getActionData(data['html'])
                self.feeds.extend(self.getFeeds(data.get('html')))
                self.getMsgList(i+1)
                i += 1
            except:
                print 'error in getRemainPage'
                continue

    @CatchException
    def getMsgList(self, page):
        '''
        获取动态加载部分的微博，每Page 分为两个Pagebar
        pagepar=0 && 1
        '''
        para = {
            'ajwvr': 6,
            'domain': 100808,
            'pl_name': 'Pl_Third_App__11',
            'id': self.tid,
            'script_uri': '/p/'+self.tid,
            'domain_op': 100808,
            '_rnd': int(time.time()),
            'feed_type': 1,
            'pagebar':0,
            'page': page,
            'pre_page': page
        }
        msglist_url = 'http://weibo.com/p/aj/v6/mblog/mbloglist'
        feeds = self.weibo.r.get(msglist_url+'?'+ self.action_data, params=para)
        html =json.loads(feeds.text)
        if html['code'] != "100000":
            return
        '''
        获取该page的feeds
        '''
        self.feeds.extend(self.getFeeds(html['data']))
        self.action_data = self.getActionData(html['data'])
        if not self.action_data:
            return

        '''
        pagebar = 1的部分
        '''
        para['pagebar'] = 1
        feeds = self.weibo.r.get(msglist_url+'?'+self.action_data, params=para)
        data = json.loads(feeds.text)['data']
        self.feeds.extend(self.getFeeds(data))
        self.action_data = self.getActionData(data)
        self.nextPage = self.getNextPage(data)


    def getHTML(self, html):
        '''
        得到js中的HTML
        '''
        return re.findall(r'<script>FM\.view\((\{"ns":"pl\.content\.homeFeed\.index.+?})\)</script>', html)


    def getNextPage(self, html):
        '''
        获取下一页连接
        '''
        W_Pages = BS(html, 'lxml').find('div', {'class': 'W_pages'})
        nextPage = W_Pages.find('a', {'bpfilter': 'page','class':'next'})
        return nextPage.get('href') if nextPage else ''

    def getActionData(self, html):
        action_data = BS(html, 'lxml').find('div', {'class':'WB_cardwrap', 'node-type':'lazyload'})
        return action_data.get('action-data') if action_data else ''

    def getFeeds(self, html):
        '''
        获取Feeds
        '''
        def feed_div(tag):
            return tag.name=="div" and tag.has_attr("tbinfo") and tag.has_attr('mid')
        html = BS(html, 'lxml')
        feeds = html.findAll(feed_div)
        return [self.getOneWeiBo(feed) for feed in feeds]

    @CatchException
    def getOneWeiBo(self, feed):
        '''
        获取微博
        '''
        mid = feed.get('mid', '')
        info = feed.find('div',class_='WB_info').find('a')
        nick = info['nick-name']
        userhref = info['href']
        feedtime = feed.find('div', class_="WB_from").find('a',{'node-type':'feed_list_item_date'})['title']

        text = feed.find('div',class_="WB_text").text
        text = re.sub(r'\s','', text)
        print mid,userhref,feedtime, nick
        comments = self.getFeedComment(mid)
        res = dict(mid=mid, text=text, feedtime=feedtime,comments=comments )
        return res

    @CatchException
    def getFeedComment(self, cid):
        '''
        获取某条微博的所有评论
        '''
        para = {
            'id': cid,
            'ajwvr': 6,
            '_rnd': (time.time())
        }
        comment_url = 'http://weibo.com/aj/v6/comment/big'
        data = self.weibo.r.get(comment_url, params=para).text
        data = json.loads(data)
        if data['code'] != "100000":
            #TODO
            return
        data = data['data']
        comments = self.getComment(BS(data['html'], 'lxml'))
        totalpage = data['page']['totalpage']
        count = data['count']
        for page in range(2, totalpage+1):
            para['page'] = page
            data = self.weibo.r.get(comment_url, params=para).text
            data = json.loads(data)
            if data['code'] != "100000":
                continue
            data = data['data']
            comments.extend(self.getComment(BS(data['html'], 'lxml')))

        return dict(count=count, currenttime=datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), comments=comments)

    @CatchException
    def getComment(self, html):
        def comment_div(tag):
            return  tag.name=='div' and tag.has_attr('comment_id')

        comments = html.findAll(comment_div)
        current_comment = []
        for comment in comments:
            cid = comment['comment_id']
            text = comment.find('div', class_="WB_text")
            info = text.find('a')
            user = info['href']
            nick = re.sub(r'\s', '', info.text)
            content = re.sub(r'\s', '',text.text).replace(nick, '', 1)[1:]
            commenttime = re.sub(r'\s', '', comment.find('div', class_="WB_from").text)
            current_comment.append(dict(comment_id=cid, userhref=user, commenttime=commenttime, content=content))
        return current_comment
