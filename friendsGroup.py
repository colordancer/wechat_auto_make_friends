#!/usr/bin/env python
# coding=utf-8

def fromRawContactList(contactList):
    result = []
    for Member in contactList:
        if Member['UserName'].find('@@') == -1:  
            continue
        if Member['NickName'].find('交友') == -1:
            continue
        result.append(Member['UserName'])
    return result