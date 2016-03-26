#!/usr/bin/env python
# coding=utf-8

from credential import Credential
import friendsGroup
import time

SYNC_INTERVAL = 30

def main():
    credential = Credential()
    if not credential.params['valid']:
        credential.refreshCredential()
    while True:
        credential.webwxsync()
        for group in credential.params['groups']:
            if friendsGroup.trySendGreeting(group, credential.params['groups'][group], credential):
                continue
            friendsGroup.trySendMaching(group, credential.params['groups'][group], credential)
        time.sleep(SYNC_INTERVAL)
    return

if __name__ == '__main__':
    main()
