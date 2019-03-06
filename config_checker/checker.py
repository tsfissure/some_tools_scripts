#coding=utf-8
'''
Created on 2019/3/5 15:35:37

@author: tys
'''

import os
import sys
import xlrd
import traceback
import ctypes


STD_OUTPUT_HANDLE= -11

FOREGROUND_RED          = 0x0c # red
FOREGROUND_DARKWHITE    = 0x07 # dark white.

std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
def set_color(color, handle=std_out_handle):
    bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
    return bool

class ConfigParam(object):

    def __init__(self):
        self.lua_path = ""
        self.xlsx_path = ""
        self.isdebug = False
        self.ignore = []

    def load(self):
        with open("checker.cfg", "r") as f:
            for line in f:
                if "lua_path" in line:
                    a, b = line[:-1].split('=')
                    self.lua_path = b.strip()
                elif "xlsx_path" in line:
                    a, b = line[:-1].split('=')
                    self.xlsx_path = b.strip()
                elif "ignore" in line:
                    a, b = line[:-1].split('=')
                    self.ignore = [i.strip() for i in b.split(',')]
        print u'lua_path: [%s]\nxlsx_path: [%s]\nignorefiles: %s\n\n' % (self.lua_path, self.xlsx_path, self.ignore)

    def isIgnore(self, fd):
        return fd in self.ignore


instCfg = ConfigParam()

class LuaTable(object):

    def __init__(self):
        self.table = {}

    def analysisRight(self, s):
        i, j = 0, 0
        left = None
        rlt = {}
        while i < len(s):
            j = i + 1
            if '{' == s[i]: # 数组/奖励
                while j < len(s) and '}' != s[j]: j += 1
                lst = [str(eval(i)) for i in s[i + 1:j].split(',')]
                tmps = "&".join(lst)
            elif '"' == s[i]: # 字符串
                while j < len(s) and '"' != s[j]: j += 1
                tmps = eval(s[i:j + 1])
            else: # 普通
                while j < len(s) and '=' != s[j] and ',' != s[j]: j += 1
                tmps = s[i:j].strip()
                if s[i] == ',': #前面一个非普通
                    tmps = tmps[1:].strip()
                if tmps.endswith("}"): #最后一个有多余
                    tmps = tmps[:-1].strip()
            if left:
                # print "[%s][%s]" % (left, tmps)
                rlt[left] = tmps
                left = None
            else:
                left = tmps
                # print u'left[%s]' % left
            i = j + 1
        return rlt

    def loadFile(self, fd):
        self.table = {}
        rlt = True
        with open(os.path.join(instCfg.lua_path, fd), "r") as f:
            for line in f:
                if 'local' in line: continue
                pos = line.find("=")
                if -1 == pos: continue
                posL = line.find('[')
                posR = line.find(']')
                key = int(line[posL + 1:posR])
                if self.table.get(key, None):
                    print u'[%s] key[%s] 重复了!!!' % (fd, key)
                    rlt = False
                    break
                right = self.analysisRight(line[pos + 2:-2])
                self.table[key] = right
        return rlt

    def get(self, i, j):
        ti = self.table.get(i, None)
        if not ti:
            return ""
        tj = ti.get(j, None)
        if not tj:
            return ""
        return tj

    def rownum(self):
        return len(self.table)


instLuaTable = LuaTable()

class XlsxTable(object):
    
    def __init__(self):
        self.data = None
        self.fdName = ""

    def loadFile(self, fd):
        pwd = os.path.join(instCfg.xlsx_path, fd)
        self.data = xlrd.open_workbook(pwd)
        self.fdName = fd

    def compareInternal(self, sheet, fd):
        if instCfg.isIgnore(fd): return True
        types = sheet.row_values(1)
        for keyName in sheet.row_values(2):
            if len(keyName) > 0 and ord(keyName[-1]) == 10:
                print u'[%s::%s] 字段[%s]结尾有回车,跳过检查' % (self.fdName, sheet.name, keyName[:-1])
                return False
        keys = [i.strip() for i in sheet.row_values(2)]
        if not instLuaTable.loadFile(fd):
            return
        if instLuaTable.rownum() + 3 != sheet.nrows:
            print u'[%s::%s] 数据行数不致! xlsx[%s] lua[%s]' % (self.fdName, sheet.name, sheet.nrows - 3,instLuaTable.rownum())
            return
        for i in xrange(3, sheet.nrows):
            try:
                vkey = int(sheet.cell(i, 0).value)
            except:
                print u'[%s::%s] 行[%s] key没有配,多余行?' % (self.fdName, sheet.name, i + 1)
                return False
            for j in xrange(1, len(types)):
                if types[j].startswith('$') or types[j] == "": continue
                val = sheet.cell(i, j).value
                luaval = instLuaTable.get(vkey, keys[j])
                check = True
                if "" == val and ("0" == luaval or "nil" == luaval or "" == luaval):
                    check = True
                elif type(val) == unicode:
                    check = True
                else:
                    try:
                        check = int(val) == int(luaval)
                    except:
                        check = str(val) == str(luaval)
                if not check:
                    print u'[%s::%s] key[%s] 列名[%s] 值不一样! xlsx[%s] lua[%s]' % (self.fdName, sheet.name, vkey, keys[j], val, luaval)
                    return False
        return True


    def compare(self, luaFiles):
        if instCfg.isIgnore(self.fdName): return
        for sheet in self.data.sheets():
            fd = sheet.name + '.lua'
            if fd in luaFiles:
                rlt = self.compareInternal(sheet, fd)
                # if not rlt:
                #     print u'[%s::%s] check FAIL!!!' % (self.fdName, sheet.name)


instXlsxTable = XlsxTable()

def lstLuaFiles():
    rlt = []
    for root, dirs, files in os.walk(instCfg.lua_path):
        for fd in files:
            if fd.endswith(".lua"):
                rlt.append(fd)
    return rlt

def lstXlsxFiles():
    rlt = []
    for root, dirs, files in os.walk(instCfg.xlsx_path):
        for fd in files:
            if fd.endswith(".xlsx") and not fd.startswith("~"):
                rlt.append(fd)
    return rlt

def gao():
    luaFiles = lstLuaFiles()
    xlsxFiles = lstXlsxFiles()
    for fd in xlsxFiles:
        try:
            print u'compare [%s]' % fd
            set_color(FOREGROUND_RED)
            instXlsxTable.loadFile(fd)
            instXlsxTable.compare(luaFiles)
            set_color(FOREGROUND_DARKWHITE)
        except:
            print u'[%s] ERROR!!!' % fd
            print traceback.print_exc(5)

if __name__ == '__main__':
    try:
        instCfg.load()
        gao()
    except :
        print traceback.print_exc(5)

    raw_input('Done!')

