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

print u'set level 60:', conn.hset('KingOfBilliards:USER','%s:lev' % uuid, 60)
print u'after set level:', conn.hget('KingOfBilliards:USER', '%s:lev' % uuid)

print u'set guide 98', conn.hset('KingOfBilliards:USER', '%s:guide' % uuid, 98)
print u'after set guide 98', conn.hget('KingOfBilliards:USER', '%s:guide' % uuid)

print u'add gm list'
isGm = conn.hget('GMList', uuid)
if not isGm:
    conn.hset('GMList', uuid, 'python script')
print conn.hget('GMList', uuid)

raw_input(u'Done!')


