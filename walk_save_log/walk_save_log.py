#coding=utf-8
'''
Created on 2019/3/11 11:38:38

@author: tys
'''

import json, os, time
import traceback
import yhjxbase64 as ybs
import codecs

class WalkSaveLog(object):

    def __init__(self):
        pass

    def init(self):
        with open("wsl.cfg", "r") as f:
            self.cfg = json.load(f)
        print self.cfg
        self.logFiles = []
        self.intvarIdLst = self.get("intvar", [])
        self.varIdLst = self.get("var", [])
        self.field = self.get("field", [])
        self.walk()

    def get(self, key, default):
        return self.cfg.get(key, default)
    
    def walk(self):
        self.logFiles = []
        for root, dirs, files in os.walk(self.get("path", ".")):
            self.logFiles += [os.path.join(root, fn) for fn in files if fn.startswith("save") and fn.endswith(".log")]

    def filterField(self, s):
        keyValues = s.split(',')
        varValue, intvarValue = "", ""
        fieldValue = {}
        for kv in keyValues:
            kvSplit = kv.split('=')
            kv0 = kvSplit[0].strip()
            if "intvar" == kv0:
                intvarValue = "=".join(kvSplit[1:])
            elif "var" == kv0:
                varValue = "=".join(kvSplit[1:])
            elif kv0 in self.field:
                fieldValue[kv0] = "=".join(kvSplit[1:])[1:-1]
        return intvarValue, varValue, fieldValue

    def decodeFieldValue(self, of, fieldValue, idLst, callback):
        if len(idLst) < 1: return
        nextInt = ybs.instance.nextInt
        ybs.instance.assign(fieldValue)
        version, size = nextInt(), nextInt()
        for i in xrange(size):
            key, value = nextInt(), callback()
            if key in idLst:
                print >> of, "[%s=%s]" % (key, value),

    def solveSaveStr(self, of, saveStr):
        print >> of, saveStr[:25].replace("T", " "),
        intvarValue, varValue, fieldValue = self.filterField(saveStr)
        self.decodeFieldValue(of, intvarValue, self.intvarIdLst, ybs.instance.nextInt)
        self.decodeFieldValue(of, varValue, self.varIdLst, ybs.instance.nextString)
        if len(fieldValue) > 0:
            json.dump(fieldValue, of, ensure_ascii = False)
        print >> of

    def visitFile(self, of, fn):
        uidKey = "player_id='%s'" % self.get("uid", 0)
        find = False
        with open(fn, "r") as f:
            saveStr = ""
            append = False
            for line in f:
                if append and not line.startswith('[20'):
                    saveStr += line[:-1]
                    continue
                if line.startswith('[20') and append:
                    self.solveSaveStr(of, saveStr)
                    find = True
                    saveStr = ""
                    append = False
                if "INSERT INTO player" in line and uidKey in line:
                    append = True
                    saveStr = line[:-1]
            if append and len(saveStr) > 0:
                self.solveSaveStr(of, saveStr)
        return find

    def visit(self):
        self.init()
        with codecs.open(time.strftime("wsl_%H.%M.%S.log", time.localtime()), "w") as of:
            for fn in self.logFiles:
                print fn
                print >> of, fn
                if self.visitFile(of, fn):
                    pass

instance = WalkSaveLog()

if __name__ == '__main__':
    try:
        instance.visit()
    except:
        traceback.print_exc(5)

    raw_input('Done!')

