#coding=utf-8
'''
Created on 2018/11/21 16:34:03

@author: tys
'''


import base_channel as bchannel
import traceback

class IdtranChannel(bchannel.BaseChannel):

    def __init__(self):
        bchannel.BaseChannel.__init__(self, "%s,%s")
        self.preName = "itemadd"

    def inputer(self, f, msg):
        print >> f, self.preName + "," + msg

    def execute(self):
        with open("idtran_yhjx.csv", "w") as f:
            preNameSet = ("itemadd", "itemrem", "itemrem", "vcadd", "vcrem")
            for i in xrange(len(preNameSet)):
                self.claerChecker()
                if i > 0:
                    print >> f, ""
                    print >> f, ""
                self.preName = preNameSet[i]
                for cpp in self.cppLst:
                    self.inputCpp(f, cpp)
                for lua in self.luaLst:
                    self.inputLua(f, lua)

instance = IdtranChannel()

if __name__ == '__main__':
    try:
        instance.loadConfig()
        instance.execute()
    except Exception, e:
        traceback.print_exc(limit = 5)
    raw_input('Done!')

