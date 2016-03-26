#!/usr/bin/env python
# coding=utf-8

def fromRawContactList(contactList, result):
    for Member in contactList:
        if Member['UserName'].find('@@') == -1:  
            continue
        if Member['NickName'].find('上海话') == -1: # test, change to 交友
            continue
        result[Member['UserName']] = {}
        for contact in Member['MemberList']:
            result[Member['UserName']][contact['UserName']] = \
                contact['NickName']
    return result