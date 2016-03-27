#!/usr/bin/env python
# coding=utf-8

from credential import Credential
import friendsGroup, subprocess, sys, termios, tty
import time

SYNC_INTERVAL = 30

def getch():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def writeToClipboard(output):
    process = subprocess.Popen(
        'pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
    process.communicate(str.encode(output, 'utf-8'))

def main():
    credential = Credential()
    if not credential.params['valid']:
        credential.refreshCredential()
    while True:
        for group in credential.params['groups']:
            msg = friendsGroup.getMaching(group, credential.params['groups'][group])
            print(msg)
            writeToClipboard(msg)
        key = getch()
        if key == 'c':
            return
        if ord(key) != 13:
            break 

    while True:
        credential.webwxsync()
        for group in credential.params['groups']:
            if friendsGroup.trySendGreeting(group, credential.params['groups'][group], credential):
                continue
            friendsGroup.trySendMaching(group, credential.params['groups'][group], credential)
        time.sleep(SYNC_INTERVAL)


if __name__ == '__main__':
    main()
