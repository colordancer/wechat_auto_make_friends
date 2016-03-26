#!/usr/bin/env python
# coding=utf-8

import os
import urllib.request, urllib.parse, urllib.error
import re
import http.cookiejar
import time
import xml.dom.minidom
import json
import sys
import math
import subprocess
import json
import threading

DEBUG = False

QRImagePath = os.getcwd() + '/qrcode.jpg'

tip = 0
uuid = ''

base_uri = ''
redirect_uri = ''

skey = ''
wxsid = ''
wxuin = ''
pass_ticket = ''
deviceId = 'e000000000000000'
SyncKey = {}
BaseRequest = {}

ContactList = []
My = []

def getUUID():
    global uuid

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

    # print data
    # window.QRLogin.code = 200; window.QRLogin.uuid = "oZwt_bFfRg==";
    regx = r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)"'
    pm = re.search(regx, str(data))

    code = pm.group(1)
    uuid = pm.group(2)

    if code == '200':
        return True

    return False


def showQRImage():
    global tip

    url = 'https://login.weixin.qq.com/qrcode/' + uuid
    params = {
        't': 'webwx',
        '_': int(time.time()),
    }

    request = urllib.request.Request(url=url, data=urllib.parse.urlencode(params).encode(encoding='UTF-8'))
    response = urllib.request.urlopen(request)

    tip = 1

    f = open(QRImagePath, 'wb')
    f.write(response.read())
    f.close()

    if sys.platform.find('darwin') >= 0:
        subprocess.call(['open', QRImagePath])
    elif sys.platform.find('linux') >= 0:
        subprocess.call(['xdg-open', QRImagePath])
    else:
        os.startfile(QRImagePath)

    print(u'请使用微信扫描二维码以登录')

def waitForLogin():
    global tip, base_uri, redirect_uri

    url = 'https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login?tip=%s&uuid=%s&_=%s' % (tip, uuid, int(time.time()))

    request = urllib.request.Request(url=url)
    response = urllib.request.urlopen(request)
    data = response.read()

    # print data

    # window.code=500;
    regx = r'window.code=(\d+);'
    pm = re.search(regx, str(data))

    code = pm.group(1)

    if code == '201':  # 已扫描
        print(u'成功扫描,请在手机上点击确认以登录')
        tip = 0
    elif code == '200':  # 已登录
        print(u'正在登录...')
        regx = r'window.redirect_uri="(\S+?)";'
        pm = re.search(regx, str(data))
        redirect_uri = pm.group(1) + '&fun=new'
        base_uri = redirect_uri[:redirect_uri.rfind('/')]
        print(base_uri)
    elif code == '408':  # 超时
        pass
    # elif code == '400' or code == '500':

    return code


def login():
    global skey, wxsid, wxuin, pass_ticket, BaseRequest

    request = urllib.request.Request(url=redirect_uri)
    response = urllib.request.urlopen(request)
    data = response.read()

    # print data

    '''
        <error>
            <ret>0</ret>
            <message>OK</message>
            <skey>xxx</skey>
            <wxsid>xxx</wxsid>
            <wxuin>xxx</wxuin>
            <pass_ticket>xxx</pass_ticket>
            <isgrayscale>1</isgrayscale>
        </error>
    '''

    doc = xml.dom.minidom.parseString(data)
    root = doc.documentElement

    for node in root.childNodes:
        if node.nodeName == 'skey':
            skey = node.childNodes[0].data
        elif node.nodeName == 'wxsid':
            wxsid = node.childNodes[0].data
        elif node.nodeName == 'wxuin':
            wxuin = node.childNodes[0].data
        elif node.nodeName == 'pass_ticket':
            pass_ticket = node.childNodes[0].data

    # print 'skey: %s, wxsid: %s, wxuin: %s, pass_ticket: %s' % (skey, wxsid, wxuin, pass_ticket)

    if skey == '' or wxsid == '' or wxuin == '' or pass_ticket == '':
        return False

    BaseRequest = {
        'Uin': int(wxuin),
        'Sid': wxsid,
        'Skey': skey,
        'DeviceID': deviceId,
    }

    return True


def webwxinit():
    global SyncKey
    url = base_uri + '/webwxinit?pass_ticket=%s&skey=%s&r=%s' % (pass_ticket, skey, int(time.time()))
    params = {
        'BaseRequest': BaseRequest
    }

    request = urllib.request.Request(url=url, data=json.dumps(params).encode('utf-8'))
    request.add_header('ContentType', 'application/json; charset=UTF-8')
    response = urllib.request.urlopen(request)
    data = response.read()

    global ContactList, My
    dic = json.loads(data.decode())
    ContactList = dic['ContactList']
    My = dic['User']

    Ret = dic['BaseResponse']['Ret']
    if Ret != 0:
        return False

    return True

def webwxgetcontact():
    print(BaseRequest)
    print(base_uri)
    MemberList = ContactList # see what happens, I'm just a coding monkey

    # 倒序遍历,不然删除的时候出问题..
    SpecialUsers = ['newsapp', 'fmessage', 'filehelper', 'weibo', 'qqmail', 'fmessage', 'tmessage', 'qmessage',
                    'qqsync', 'floatbottle', 'lbsapp', 'shakeapp', 'medianote', 'qqfriend', 'readerapp', 'blogapp',
                    'facebookapp', 'masssendapp', 'meishiapp', 'feedsapp', 'voip', 'blogappweixin', 'weixin',
                    'brandsessionholder', 'weixinreminder', 'wxid_novlwrv3lqwv11', 'gh_22b87fa7cb3c',
                    'officialaccounts', 'notification_messages', 'wxid_novlwrv3lqwv11', 'gh_22b87fa7cb3c', 'wxitil',
                    'userexperience_alarm', 'notification_messages']
    print(len(MemberList))
    for i in range(len(MemberList) - 1, -1, -1):
        Member = MemberList[i]
        if Member['VerifyFlag'] & 8 != 0:  # 公众号/服务号
            MemberList.remove(Member)
        elif Member['UserName'] in SpecialUsers:  # 特殊账号
            MemberList.remove(Member)
        elif Member['UserName'].find('@@') != -1:  # 群聊
            MemberList.remove(Member)
        elif Member['UserName'] == My['UserName']:  # 自己
            MemberList.remove(Member)

    return MemberList

# 根据指定的Username发消息
def sendMsg(MyUserName, ToUserName, msg):
    url = base_uri + '/webwxsendmsg?pass_ticket=%s' % (pass_ticket)
    params = {
        "BaseRequest": BaseRequest,
        "Msg": {"Type": 1, "Content": msg, "FromUserName": MyUserName, "ToUserName": ToUserName},
    }

    json_obj = json.dumps(params,ensure_ascii=False).encode('utf-8')#ensure_ascii=False防止中文乱码
    request = urllib.request.Request(url=url, data=json_obj)
    request.add_header('ContentType', 'application/json; charset=UTF-8')
    urllib.request.urlopen(request)

def loginProcess():
    print(u'欢迎使用情怀版微信，正在生成登录二维码...')

    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    urllib.request.install_opener(opener)

    if not getUUID():
        print(u'获取uuid失败')
        return

    showQRImage()
    time.sleep(1)

    while waitForLogin() != '200':
        pass

    os.remove(QRImagePath)

    if not login():
        print(u'登录失败')
        return

    if not webwxinit():
        print(u'初始化失败')
        return

    MemberList = webwxgetcontact()
    MemberCount = len(MemberList)

def main():
    return

if __name__ == '__main__':
    main()
