#!/usr/bin/env python
# coding=utf-8

from credential import Credential
import friendsGroup
import time

SYNC_INTERVAL = 5

def main():
    credential = Credential()
    credential.refreshCredential()
    while True:
        credential.webwxsync()
        for group in credential.params['groups']:
            friendsGroup.trySendGreeting(credential.params['groups'][group], credential)
        time.sleep(SYNC_INTERVAL)
    return

if __name__ == '__main__':
    main()
