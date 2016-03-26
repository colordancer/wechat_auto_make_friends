#!/usr/bin/env python
# coding=utf-8

FILE_NAME = 'questions.txt'
def load():
    with open(FILE_NAME) as f:
        q_list = str(f.read()).split('\n')
        q_list = filter(bool, q_list)
        return list(q_list)