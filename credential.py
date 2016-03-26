#!/usr/bin/env python
# coding=utf-8
import json, os, urllib, time, http, re, sys, subprocess, xml, friendsGroup, Sync
import urllib.request, urllib.parse, urllib.error, http.cookiejar, xml.dom.minidom

class Credential():
    CREDENTIAL_FILE = 'credential'
    MAX_CONNECTION_FAIL = 3

    def __init__(self):
        self.clearParams()
        self.QRImagePath = os.getcwd() + '/qrcode.jpg'
        self.tip = 0
        self.failcount = 0
        self.tryLoadDataFromFile()

    def clearParams(self):
        self.params = {
            'uuid': '',
            'base_uri': '',
            'redirect_uri': '',
            'skey': '',
            'wxsid': '',
            'wxuin': '',
            'pass_ticket': '',
            'deviceId': 'e000000000000000',
            'groups': {},
            'myUserName': '',
            'valid': False,
            'synckey': {'List': [], 'Count': 0},
        }

    def tryLoadDataFromFile(self):
        try:
            with open(self.CREDENTIAL_FILE) as f:
                self.params = json.load(f)
        except:
            pass

    def refreshUUID(self):
        url = 'https://login.weixin.qq.com/jslogin'
        params = {
            'appid': 'wx782c26e4c19acffb',
            'fun': 'new',
            'lang': 'zh_CN',
            '_': int(time.time()),
        }

        request = urllib.request.Request(url=url, data=urllib.parse.urlencode(params).encode(encoding='UTF8'))
        response = urllib.request.urlopen(request)
        data = response.read()

        regx = r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)"'
        pm = re.search(regx, str(data))

        code = pm.group(1)
        self.params['uuid'] = pm.group(2)

        if code == '200':
            return True

        return False


    def showQRImage(self):
        url = 'https://login.weixin.qq.com/qrcode/' + self.params['uuid']
        params = {
            't': 'webwx',
            '_': int(time.time()),
        }

        request = urllib.request.Request(url=url, data=urllib.parse.urlencode(params).encode(encoding='UTF-8'))
        response = urllib.request.urlopen(request)

        self.tip = 1
        f = open(self.QRImagePath, 'wb')
        f.write(response.read())
        f.close()

        if sys.platform.find('darwin') >= 0:
            subprocess.call(['open', self.QRImagePath])
        elif sys.platform.find('linux') >= 0:
            subprocess.call(['xdg-open', self.QRImagePath])
        else:
            os.startfile(self.QRImagePath)

        print(u'请使用微信扫描二维码以登录')

    def waitForLogin(self):

        url = 'https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login?tip=%s&uuid=%s&_=%s' % \
            (self.tip, self.params['uuid'], int(time.time()))

        request = urllib.request.Request(url=url)
        response = urllib.request.urlopen(request)
        data = response.read()

        regx = r'window.code=(\d+);'
        pm = re.search(regx, str(data))

        code = pm.group(1)

        if code == '201':  # 已扫描
            print(u'成功扫描,请在手机上点击确认以登录')
            self.tip = 0
        elif code == '200':  # 已登录
            print(u'正在登录...')
            regx = r'window.redirect_uri="(\S+?)";'
            pm = re.search(regx, str(data))
            self.params['redirect_uri'] = pm.group(1) + '&fun=new'
            self.params['base_uri'] = self.params['redirect_uri'][:self.params['redirect_uri'].rfind('/')]
        elif code == '408':  # 超时
            pass

        return code


    def login(self):
        request = urllib.request.Request(url=self.params['redirect_uri'])
        response = urllib.request.urlopen(request)
        data = response.read()

        doc = xml.dom.minidom.parseString(data)
        root = doc.documentElement

        for node in root.childNodes:
            if node.nodeName == 'skey':
                self.params['skey'] = node.childNodes[0].data
            elif node.nodeName == 'wxsid':
                self.params['wxsid'] = node.childNodes[0].data
            elif node.nodeName == 'wxuin':
                self.params['wxuin'] = node.childNodes[0].data
            elif node.nodeName == 'pass_ticket':
                self.params['pass_ticket'] = node.childNodes[0].data

        # print 'skey: %s, wxsid: %s, wxuin: %s, pass_ticket: %s' % (skey, wxsid, wxuin, pass_ticket)

        if self.params['skey'] == '' or self.params['wxsid'] == '' or \
            self.params['wxuin'] == '' or self.params['pass_ticket'] == '':
            return False

        return True

    def getBaseRequest(self):
        return {
            'Uin': int(self.params['wxuin']),
            'Sid': self.params['wxsid'],
            'Skey': self.params['skey'],
            'DeviceID': self.params['deviceId'],
        }


    def webwxinit(self):
        url = self.params['base_uri'] + '/webwxinit?pass_ticket=%s&skey=%s&r=%s' % \
            (self.params['pass_ticket'], self.params['skey'], int(time.time()))
        params = {
            'BaseRequest': self.getBaseRequest()
        }

        request = urllib.request.Request(url=url, data=json.dumps(params).encode('utf-8'))
        request.add_header('ContentType', 'application/json; charset=UTF-8')
        response = urllib.request.urlopen(request)
        data = response.read()

        dic = json.loads(data.decode())
        ContactList = dic['ContactList']
        My = dic['User']
        self.params['myUserName'] = My['UserName']
        self.params['synckey'] = dic['SyncKey']

        friendsGroup.fromRawContactList(ContactList, self.params['groups'])

        Ret = dic['BaseResponse']['Ret']
        if Ret != 0:
            return False

        return True

    def refreshCredential(self):
        self.clearParams()
        with open(self.CREDENTIAL_FILE, 'w') as f:
            f.write('')

        print(u'欢迎使用情怀版微信，正在生成登录二维码...')

        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        urllib.request.install_opener(opener)

        if not self.refreshUUID():
            print(u'获取uuid失败')
            self.params['valid'] = False
            return

        self.showQRImage()
        time.sleep(1)

        while self.waitForLogin() != '200':
            pass

        os.remove(self.QRImagePath)

        if not self.login():
            print(u'登录失败')
            self.params['valid'] = False
            return

        if not self.webwxinit():
            print(u'初始化失败')
            self.params['valid'] = False
            return

        self.params['valid'] = True

        self.getContactList()

        for groupUserName in self.params['groups']:
            self.getGroupMember(groupUserName)

        self.writeToFile()

    def getGroupMember(self, groupUserName):
        url = self.params['base_uri'] + '/webwxbatchgetcontact?type=ex&pass_ticket=%s&skey=%s&r=%s' % \
            (self.params['pass_ticket'], self.params['skey'], int(time.time()))
        params = {
            "BaseRequest": self.getBaseRequest(),
            "Count": 1,
            "List": [{"UserName": groupUserName}],
        }

        json_obj = json.dumps(params,ensure_ascii=False).encode('utf-8')#ensure_ascii=False防止中文乱码
        request = urllib.request.Request(url=url, data=json_obj)

        request.add_header('ContentType', 'application/json; charset=UTF-8')
        response = urllib.request.urlopen(request)
        data = response.read()
        data = data.decode('utf-8', 'replace')

        dic = json.loads(data)
        MemberList = dic['ContactList']
        friendsGroup.fromRawContactList(MemberList, self.params['groups'])


    def getContactList(self):
        url = self.params['base_uri'] + '/webwxgetcontact?pass_ticket=%s&skey=%s&r=%s' % \
            (self.params['pass_ticket'], self.params['skey'], int(time.time()))

        request = urllib.request.Request(url=url)
        request.add_header('ContentType', 'application/json; charset=UTF-8')
        response = urllib.request.urlopen(request)
        data = response.read()

        data = data.decode('utf-8', 'replace')

        dic = json.loads(data)
        MemberList = dic['MemberList']

        friendsGroup.fromRawContactList(MemberList, self.params['groups'])

        # 根据指定的Username发消息
    def sendMsg(self, ToUserName, msg):
        url = self.params['base_uri'] + '/webwxsendmsg?pass_ticket=%s' % \
            (self.params['pass_ticket'])
        params = {
            "BaseRequest": self.getBaseRequest(),
            "Msg": {
                "Type": 1, 
                "Content": msg, 
                "FromUserName": self.params['myUserName'], 
                "ToUserName": ToUserName},
        }

        json_obj = json.dumps(params,ensure_ascii=False).encode('utf-8')#ensure_ascii=False防止中文乱码
        request = urllib.request.Request(url=url, data=json_obj)
        request.add_header('ContentType', 'application/json; charset=UTF-8')
        response = urllib.request.urlopen(request)
        data = response.read()
        data = data.decode('utf-8', 'replace')
        dic = json.loads(data)
        if not dic['MsgID']:
            self.onTunnelFail()

    def webwxsync(self):
        url = self.params['base_uri'] + '/webwxsync?pass_ticket=%s&skey=%s&r=%s' % \
            (self.params['pass_ticket'], self.params['skey'], int(time.time()))
        params = {
            "BaseRequest": self.getBaseRequest(),
            "SyncKey": self.params['synckey'],
        }

        json_obj = json.dumps(params,ensure_ascii=False).encode('utf-8')#ensure_ascii=False防止中文乱码
        request = urllib.request.Request(url=url, data=json_obj)

        request.add_header('ContentType', 'application/json; charset=UTF-8')
        response = urllib.request.urlopen(request)
        data = response.read()
        data = data.decode('utf-8', 'replace')
        dic = json.loads(data)
        Sync.updateKey(self.params['synckey'], dic['SyncKey'])
        if dic['SyncKey']['Count'] == 0:
            self.onTunnelFail()
        friendsGroup.fromRawContactList(dic['ModContactList'], self.params['groups'])
        for newMessage in dic['AddMsgList']:
            if newMessage['FromUserName'] in self.params['groups']:
                group = self.params['groups'][newMessage['FromUserName']]
                newMember = friendsGroup.findNewMember(newMessage['Content'])
                if newMember:
                    group['newMember'][newMember] = True
                    continue # do not update last update time
                group['update'] = max(group['update'], newMessage['CreateTime'])
        self.writeToFile()

    def onTunnelFail(self):
        self.failcount += 1
        if self.failcount > self.MAX_CONNECTION_FAIL:
            self.refreshCredential()
            self.failcount = 0

    def writeToFile(self):
        with open(self.CREDENTIAL_FILE, 'w') as f:
            f.write(json.dumps(self.params))


