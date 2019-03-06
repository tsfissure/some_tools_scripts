#coding=utf-8
'''
Created on 2018/11/8 15:05:49

@author: tys
'''

import base_channel as bchannel
import traceback
import time

class LocalChannel(bchannel.BaseChannel):

    def __init__(self):
        bchannel.BaseChannel.__init__(self, "%s=%s")

    def execute(self):
        tm = time.localtime()
        with open("local_channel_%02d%02d.cfg" % (tm.tm_mon, tm.tm_mday), "w") as f:
            for cpp in self.cppLst:
                self.inputCpp(f, cpp)
            for lua in self.luaLst:
                self.inputLua(f, lua)


instance = LocalChannel()

if __name__ == '__main__':
    try:
        instance.loadConfig()
        instance.execute()
    except Exception, e:
        traceback.print_exc(limit = 5)
    raw_input('Done!')

