#coding=utf-8
'''
Created on 2018/4/8 11:11:22

@author: tys
'''

import redis



conn = redis.Redis(host = 'localhost', port = 6379, db = 0)

name = raw_input('input your name:')
uuid = conn.get('KingOfBilliards:nick:' + name)
print u'uuid:', uuid

if not uuid:
    print u'no user'
    exit(0)
	
diamond = input('input diamond:')

print u'set diamond 98', conn.hset('KingOfBilliards:USER', '%s:diamond' % uuid, diamond)
print u'after set diamond 98', conn.hget('KingOfBilliards:USER', '%s:guide' % uuid)

raw_input(u'Done!')


