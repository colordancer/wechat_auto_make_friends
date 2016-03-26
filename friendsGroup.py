#!/usr/bin/env python
# coding=utf-8
import time

QUITE_INTERVAL = 10 # testing, change to 10 * 60

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

def trySendGreeting(group, credential):
    if not group['newMember']:
        return
    if time.time() - group['update'] < QUITE_INTERVAL:
        return
    credential.