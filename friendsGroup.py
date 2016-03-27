#!/usr/bin/env python
# coding=utf-8
import time, random, re, Questions

QUITE_INTERVAL = 5 * 60 # testing, change to 10 * 60
questions = Questions.load()

def findNewMember(content):
    regx = r'は(\S+?)さんをグループチャットに招待しました'
    pm = re.search(regx, content)
    if pm:
        return pm.group(1)
    regx = r'(\S+?)さんは'
    pm = re.search(regx, content)
    if pm:
        return pm.group(1)

def fromRawContactList(contactList, result):
    for Member in contactList:
        if Member['UserName'].find('@@') == -1:  
            continue
        if Member['NickName'].find('交友') == -1: 
            continue
        users = {}
        for contact in Member['MemberList']:
            users[contact['UserName']] = \
                contact['NickName']
        if not Member['UserName'] in result:
            result[Member['UserName']] = {
                'users': {},
                'update': 0,
                'newMember': {},
            }
        result[Member['UserName']]['users'] = users

def trySendGreeting(groupName, group, credential):
    print("trySendGreeting")
    if not group['newMember']:
        return False
    if time.time() - group['update'] < QUITE_INTERVAL:
        return False
    print('SendGreeting')
    person = list(group['newMember'].keys())[0]
    del group['newMember'][person]
    msg = '@' + person + ', 欢迎欢迎。' + random.choice(questions)
    credential.sendMsg(groupName, msg)
    group['update'] = time.time()
    return True

def getMaching(groupName, group):
    people = random.sample(set(group['users'].values()), 2)
    ques = random.choice(questions)
    return '@' + people[0] + ', ' + ques + '\n' + \
        '@' + people[1] + ', ' + ques

def sendMaching(groupName, group, credential):
    print("SendMaching")
    msg = getMaching(groupName, group)
    credential.sendMsg(groupName, msg)
    group['update'] = time.time()
    return True
    
def trySendMaching(groupName, group, credential):
    print("trySendMaching")
    for user in list(group['users'].keys()):
        if group['users'][user] in ['阿云', '八戒', 'Yunzhi']:
            del group['users'][user]
    if len(group['users']) < 2:
        return False
    if time.time() - group['update'] < QUITE_INTERVAL:
        return False
    return sendMaching(groupName, group, credential)