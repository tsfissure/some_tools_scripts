#coding=utf-8
'''
Created on 2018/12/11 15:36:35

@author: tys
'''

import base64


class BasicData(object):

    def __init__(self):
        self.pos = 0
        self.decodeStr = ""

    def load(self):
        oriStr = ""
        with open("data.cfg", "r") as f:
            oriStr = f.read()
        self.decodeStr = base64.b64decode(oriStr.strip())

    def assign(self, s):
        self.decodeStr = base64.b64decode(s.strip(), "!-")
        self.pos = 0

    def getPosValue(self, pos):
        return ord(self.decodeStr[pos]) & 0xff

    def nextInt(self):
        rlt = (self.getPosValue(self.pos + 3) << 24) + (self.getPosValue(self.pos + 2) << 16) + (self.getPosValue(self.pos + 1) << 8) + self.getPosValue(self.pos)
        self.pos += 4
        return rlt

    def nextLong(self):
        low = self.nextInt()
        high = self.nextInt()
        return (high << 32) + low

    def nextString(self):
        l = self.pos
        while True:
            val = self.getPosValue(self.pos)
            self.pos += 1
            if 0 == val:
                break
        return self.decodeStr[l:self.pos - 1]

    def nextShort(self):
        rlt = (self.getPosValue(self.pos + 1) << 8) + self.getPosValue(self.pos)
        self.pos += 2
        return rlt
        
    def display(self, callback):
        callback(self)

    def hasValue(self):
        return self.pos < len(self.decodeStr)

instance = BasicData()

if __name__ == '__main__':
    pass

