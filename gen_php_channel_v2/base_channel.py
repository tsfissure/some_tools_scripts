#coding=utf-8
'''
Created on 2018/11/21 16:27:30

@author: tys
'''

import codecs

class BaseChannel(object):

    def __init__(self, msgFmt):
        self.msgFmt = msgFmt
        self.cppLst = []
        self.luaLst = []
        self.checkIdMap = {}

    def loadConfig(self):
        cppPath = ""
        luaPath = ""
        with open("path.cfg", "r") as f:
            for line in f:
                if line.startswith("cpp="):
                    cppPath = line[4:-1]
                elif line.startswith("lua="):
                    luaPath = line[4:-1]
        with codecs.open(cppPath, encoding = 'GB2312') as f:
            cppstart = False
            for line in f:
                if '^pass' in line: continue
                if "enum CommonChannel" in line:
                    cppstart = True
                    continue
                if not cppstart: continue
                if "};" in line:
                    break
                msg = line[:-1]
                self.cppLst.append(msg.encode("UTF-8"))
        with codecs.open(luaPath, encoding = 'UTF-8') as f:
            for line in f:
                msg = line[:-1]
                self.luaLst.append(msg.encode("UTF-8"))

    def inputer(self, f, msg):
        print >> f, msg

    def checkChannelId(self, cid):
        assert not self.checkIdMap.get(cid, None), "channel[%s] duplicate" % cid
        self.checkIdMap[cid] = cid

    def claerChecker(self):
        self.checkIdMap = {}

    def inputLua(self, f, line):
        if '^pass' in line: return
        lst = line[:-1].split('=')
        if len(lst) < 2: return
        lst1 = lst[1].split('--') 
        if len(lst1) < 2: return
        lst2 = lst1[1].split('&')
        if len(lst2) > 1:
            lst3 = lst2[1].split(']')[0].strip()
            key = [i for i in lst3.split(',')]
            basic = int(lst1[0].strip())
            self.checkChannelId(basic)
            msg = self.msgFmt % (basic, lst2[0].strip())
            self.inputer(f, msg)
            for k in key:
                if "-" in k:
                    a, b = [int(i) for i in k[1:].split('-')]
                    for i in xrange(a, b + 1):
                        cid = basic * 1000 + i
                        self.checkChannelId(cid)
                        msg = self.msgFmt % (cid, lst2[0].strip() + "_" + str(i))
                        self.inputer(f, msg)
                else:
                    kk = k[1:] if k.startswith("[") else k
                    cid = basic*1000 + int(kk)
                    self.checkChannelId(cid)
                    msg = self.msgFmt % (cid, lst2[0].strip() + "_" + kk)
                    self.inputer(f, msg)
        else:
            cid = lst1[0].strip()
            self.checkChannelId(cid)
            msg = self.msgFmt % (cid, lst1[1].strip())
            self.inputer(f, msg)

    def inputCpp(self, f, line):
        if '^pass' in line: return
        lst = line[:-1].split('=')
        if len(lst) > 1:
            lst1 = lst[1].split('//') 
            if len(lst1) < 2: return
            lst2 = lst1[1].split('&')
            if len(lst2) > 1:
                lst2[1] = lst2[1].strip()
                lst3 = lst2[1].split('][')
                if len(lst3) > 1:
                    key = [int(i) for i in lst3[0][1:].split(',')]
                    val = lst3[1][:-1].split(',')
                    if len(key) == len(val):
                        basic = int(lst1[0].strip())
                        for i in xrange(len(key)):
                            k = int(key[i])
                            v = val[i]
                            msg = self.msgFmt % (basic*1000+k, v)
                            self.checkChannelId(k)
                            self.inputer(f, msg)
                else:
                    cid = lst1[0].strip()[:-1]
                    self.checkChannelId(cid)
                    msg = self.msgFmt % (cid, lst1[1].strip())
                    self.inputer(msg)
            else:
                cid = lst1[0].strip()[:-1]
                self.checkChannelId(cid)
                msg = self.msgFmt % (cid, lst1[1].strip())
                self.inputer(f, msg)

