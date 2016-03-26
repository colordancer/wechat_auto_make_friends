#!/usr/bin/env python
# coding=utf-8

def fromRawContactList(contactList):
    for Member in contactList:
        if Member['UserName'].find('@@') == -1:  
            continue
        print(Member['UserName'])
        print(Member)