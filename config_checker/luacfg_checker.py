#coding=utf-8
'''
Created on 2019/4/1 11:19:29

@author: tys
'''
import os
import sys
import xlrd
import traceback
import ctypes
import csv
import codecs

import cfg_reader as cfg

STD_OUTPUT_HANDLE= -11

FOREGROUND_RED          = 0x0c # red
FOREGROUND_DARKWHITE    = 0x07 # dark white.

std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
def set_color(color, handle=std_out_handle):
    bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
    return bool

class LuaTable(object):

    spliter = (":", "|", ",", "-")

    def __init__(self):
        self.table = {}
        self.fdName = ""
        self.analysisString = ""
        self.analysisKey = 0

    def checkList(self, lst, spt):
        if not spt:
            for i in lst:
                try:
                    int(i)
                except:
                    print u"[%s] 解析失败,key[%s]字符串分隔出错[%s]!" % (self.fdName, self.analysisKey, i)
                    return False
            return True
        for i in lst:
            si = i.split(spt)
            for j in si:
                try:
                    int(j)
                except:
                    print u"[%s] 解析失败,key[%s]字符串分隔出错[%s]!" % (self.fdName, self.analysisKey, i)
                    return False
        return True

    def analysisRight(self, s):
        self.analysisString = s
        i, j = 0, 0
        left = None
        rlt = {}
        while i < len(s):
            j = i + 1
            if '{' == s[i]: # 数组/奖励
                while j < len(s) and '}' != s[j]: j += 1
                lst = [str(eval(k)) for k in s[i + 1:j].split(',')]
                if len(lst) > 0:
                    spt = next((k for k in self.spliter if k in lst[0]), None)
                    if not self.checkList(lst, spt): return None
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
        self.fdName = fd
        self.table = {}
        rlt = True
        with open(os.path.join(cfg.instCfg.lua_path, fd), "r") as f:
            for line in f:
                if 'local' in line: continue
                pos = line.find("=")
                if -1 == pos: continue
                posL = line.find('[')
                posR = line.find(']')
                try:
                    key = int(line[posL + 1:posR])
                except:
                    print u'[%s] 解析失败,格式不标准!' % fd
                    rlt = False
                    break
                if self.table.get(key, None):
                    print u'[%s] key[%s] 重复了!!!' % (fd, key)
                    rlt = False
                    break
                self.analysisKey = key
                right = self.analysisRight(line[pos + 2:-2])
                if right: self.table[key] = right
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

def gao():
    for fd in cfg.instCfg.luaFiles:
        try:
            set_color(FOREGROUND_DARKWHITE)
            print u'[%s]' % fd
            set_color(FOREGROUND_RED)
            instLuaTable.loadFile(fd)
        except:
            print u'[%s] ERROR!!!' % fd
            print traceback.print_exc(5)

if __name__ == '__main__':
    try:
        cfg.instCfg.load()
        cfg.instCfg.loadFiles()
        gao()
    except :
        print traceback.print_exc(5)

    set_color(FOREGROUND_DARKWHITE)
    raw_input('Done!')

