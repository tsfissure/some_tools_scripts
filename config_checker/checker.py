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
import csv
import codecs


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
        self.csv_path = ""
        self.isdebug = False
        self.ignore = []
        self.luaFiles = []
        self.csvFiles = []
        self.xlsxFiles = []

    def load(self):
        with open("checker.cfg", "r") as f:
            for line in f:
                if "lua_path" in line:
                    a, b = line[:-1].split('=')
                    self.lua_path = b.strip()
                elif "xlsx_path" in line:
                    a, b = line[:-1].split('=')
                    self.xlsx_path = b.strip()
                elif "csv_path" in line:
                    a, b = line[:-1].split('=')
                    self.csv_path = b.strip()
                elif "ignore" in line:
                    a, b = line[:-1].split('=')
                    self.ignore = [i.strip() for i in b.split(',')]
            print u'lua_path: [%s]\ncsv_path: [%s]\nxlsx_path: [%s]\nignorefiles: %s\n\n' % (self.lua_path, self.csv_path, self.xlsx_path, self.ignore)

    def isIgnore(self, fd):
        return fd in self.ignore

    def loadFilesInternal(self, path, suffix):
        rlt = []
        for root, dirs, files in os.walk(path):
            rlt += [fd for fd in files if fd.endswith(suffix) and not fd.startswith("~") and not self.isIgnore(fd)]
        return rlt

    def loadFiles(self):
        self.luaFiles = self.loadFilesInternal(self.lua_path, ".lua")
        self.csvFiles = self.loadFilesInternal(self.csv_path, ".csv")
        self.xlsxFiles = self.loadFilesInternal(self.xlsx_path, ".xlsx")

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


class CsvTable(object):

    def __init__(self):
        self.data = []

    def loadFile(self, fd):
        self.data = []
        with codecs.open(os.path.join(instCfg.csv_path, fd), "r") as f:
            try:
                reader = csv.reader(f)
                self.data = [row for row in reader]
                # print self.data
            except:
                print u'解析[%s] 出错!' % fd
                print traceback.print_exc(5)
                return False
        return True

    def rownum(self):
        return len(self.data)

    def colnum(self):
        if 0 == len(self.data):
            return 0
        return len(self.data[0])

    def get(self, i, j):
        return self.data[i][j]

instCsvTable = CsvTable()

class XlsxTable(object):

    def __init__(self):
        self.data = None
        self.fdName = ""

    def loadFile(self, fd):
        pwd = os.path.join(instCfg.xlsx_path, fd)
        self.data = xlrd.open_workbook(pwd)
        self.fdName = fd

    def compareLua(self, sheet, fd):
        types = sheet.row_values(1)
        for keyName in sheet.row_values(2):
            if len(keyName) > 0 and ord(keyName[-1]) == 10:
                print u'[%s::%s] 字段[%s]结尾有回车,跳过检查' % (self.fdName, sheet.name, keyName[:-1])
                return
        if not instLuaTable.loadFile(fd):
            return
        if instLuaTable.rownum() + 3 != sheet.nrows:
            print u'[%s::%s] 数据行数不致! xlsx[%s] lua[%s]' % (self.fdName, sheet.name, sheet.nrows - 3,instLuaTable.rownum())
            return
        keys = [i.strip() for i in sheet.row_values(2)]
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

    def compareCsv(self, sheet, fd):
        if not instCsvTable.loadFile(fd):
            return False
        if instCsvTable.rownum() < sheet.nrows:
            print u'[%s::%s]与csv行不一样多!xlsx[%s] csv[%s]' % (self.fdName, sheet.name, sheet.nrows, instCsvTable.rownum())
            return False
        keys = [i.strip() for i in sheet.row_values(2)]
        for i in xrange(sheet.nrows):
            try:
                vkey = int(sheet.cell(i, 0).value)
            except:
                vkey = i
            for j in xrange(sheet.ncols):
                val =  sheet.cell(i, j).value 
                if unicode == type(val): continue
                csvVal = instCsvTable.get(i, j)
                check = True
                try:
                    check = int(val) == int(csvVal)
                except:
                    check = str(val) == str(csvVal)
                if not check:
                    print u'[%s::%s]与csv key[%s] 列[%s] 值不一样! xlsx[%s] csv[%s]' % (self.fdName, sheet.name, vkey, keys[j], val, csvVal)
                    return False
        return True

    def compare(self):
        for sheet in self.data.sheets():
            fd = sheet.name + '.lua'
            if fd in instCfg.luaFiles:
                if not self.compareLua(sheet, fd):
                    continue
            fd = sheet.name + '.csv'
            if fd in instCfg.csvFiles:
                rlt = self.compareCsv(sheet, fd)


instXlsxTable = XlsxTable()

def gao():
    for fd in instCfg.xlsxFiles:
        # if fd != "demonstepTable.xlsx": continue
        try:
            set_color(FOREGROUND_DARKWHITE)
            print u'compare [%s]' % fd
            set_color(FOREGROUND_RED)
            instXlsxTable.loadFile(fd)
            instXlsxTable.compare()
        except:
            print u'[%s] ERROR!!!' % fd
            print traceback.print_exc(5)

if __name__ == '__main__':
    try:
        instCfg.load()
        instCfg.loadFiles()
        gao()
    except :
        print traceback.print_exc(5)

    set_color(FOREGROUND_DARKWHITE)
    raw_input('Done!')

