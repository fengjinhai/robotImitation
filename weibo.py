#!/usr/bin/env python
# encoding: utf-8

import requests
import base64, rsa, binascii
import time, re, json, random
import sys
sys.path.append('../lib')
from yunsu import APIClient 

class Weibo(object):
    '''
    weibo class:
       - login
       -
    '''
    def __init__(self, username="", passwd="", proxy=False):
        self.r = requests.Session()
        self.client = APIClient()
        if proxy:
            self.r.proxies={
                'http': 'socks5://127.0.0.1:1080',
                'https': 'socks5://127.0.0.1:1080',
            }
        self.username = username
        self.passwd = passwd
        self.weibo_url = 'http://weibo.com/'
        self.prelogin_url = 'https://login.sina.com.cn/sso/prelogin.php'
        self.login_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.23 Mobile Safari/537.36'}
        pass

    def login(self):
        '''
        '''
        self.prelogin()
        self.sp = self.getPwd()
        para = {
            "encoding": "UTF-8",
            "entry": "weibo",
            "from": "",
            "gateway": 1,
            "nonce": self.nonce,
            "pagerefer": "http://login.sina.com.cn/sso/logout.php?entry=miniblog&r=http%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl%3D%252F",
            "prelt": 117,
            "pwencode": "rsa2",
            "returntype": "TEXT",
            "rsakv": self.rsakv,
            "savestate": 0,
            "servertime": self.servertime,
            "service": "miniblog",
            "sp": self.sp,
            "sr": "1920*1080",
            "su": self.su,
            "url": "http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack",
            "useticket": 1,
            "vsnf": 1,
        }

        if self.showpin == 1:
            vcode = self.getPin()
            #vcode = raw_input('input vcode:')
            para['door'] = vcode
            para['cdult'] = 2
            para['pcid'] = self.pcid
            para['prelt'] = 2041
        data = self.r.post(self.login_url, data=para, headers=self.headers)
        data = json.loads(data.text)
        if data['retcode'] != "0":
            return False, data['reason']


        self.ticket = data['ticket']
        para={
            'callback':'sinaSSOController.callbackLoginStatus',
            'ticket': self.ticket,
            'client': 'ssologin.js(v1.4.18)',
            'retcode': 0,
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack&sudaref=weibo.com'
        }
        self.r.get('http://passport.weibo.com/wbsso/login', params=para, headers=self.headers)
        self.r.get(para['url'], headers=self.headers)
        interest = self.r.get('http://weibo.com/nguide/interest')
        uid = re.search(r"CONFIG\['uid'\]='([^']+)'", interest.text).group(1)
        nick = re.search(r"CONFIG\['nick'\]='([^']+)'", interest.text).group(1)
        return True, uid, nick

    def getPin(self):
        '''
        验证码
        '''
        para = {
            'p': self.pcid,
            'r': random.randint(10000,100000),
            's': 0
        }
        pic = self.r.get('http://login.sina.com.cn/cgi/pin.php', params=para, headers=self.headers)
        imgPath = './pin.png'
        file(imgPath, 'wb').write(pic.content)
        return self.client.shibie(imgPath)

    def prelogin(self):
        '''
        prelogin process
        '''
        self.r.get(self.weibo_url)
        self.su = self.getSu()
        para = {
            "_": time.time(),
            "callback": "sinaSSOController.preloginCallBack",
            "checkpin": 1,
            "client": "ssologin.js(v1.4.18)",
            "entry": "weibo",
            "rsakt": "mod",
            "su": self.su
        }
        d = self.r.get(self.prelogin_url, params=para, headers=self.headers).text
        data = re.findall(r'preloginCallBack\(([\w\W]+?)\)', d)[0]
        data = json.loads(data)
        self.servertime = data.get('servertime','')
        self.nonce = data.get('nonce', '')
        self.pubkey = data.get('pubkey', '')
        self.rsakv = data.get('rsakv', '')
        self.showpin = data.get('showpin', 0)
        self.pcid = data.get('pcid', '')

    def getSu(self):
        '''
        获取加密用户名: 只有 Base64
        '''
        return  base64.encodestring(self.username)[:-1]

    def getPwd(self):
        '''
        获取加密密码sp
        '''
        rsaPubkey = int(self.pubkey, 16)
        RSAKey = rsa.PublicKey(rsaPubkey, 65537) #创建公钥
        codeStr = str(self.servertime) + '\t' + str(self.nonce) + '\n' + str(self.passwd)
        pwd = rsa.encrypt(codeStr, RSAKey)  #使用rsa进行加密
        return binascii.b2a_hex(pwd)  #将加密信息转换为16进制。
