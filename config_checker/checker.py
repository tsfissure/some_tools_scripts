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

import luacfg_checker as lc
import cfg_reader as cfg


STD_OUTPUT_HANDLE= -11

FOREGROUND_RED          = 0x0c # red
FOREGROUND_DARKWHITE    = 0x07 # dark white.

std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
def set_color(color, handle=std_out_handle):
    bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
    return bool

class CsvTable(object):

    def __init__(self):
        self.data = []

    def loadFile(self, fd):
        self.data = []
        with codecs.open(os.path.join(cfg.instCfg.csv_path, fd), "r") as f:
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
        pwd = os.path.join(cfg.instCfg.xlsx_path, fd)
        self.data = xlrd.open_workbook(pwd)
        self.fdName = fd

    def compareLua(self, sheet, fd):
        types = sheet.row_values(1)
        for keyName in sheet.row_values(2):
            if len(keyName) > 0 and ord(keyName[-1]) == 10:
                print u'[%s::%s] 字段[%s]结尾有回车,跳过检查' % (self.fdName, sheet.name, keyName[:-1])
                return
        if not lc.instLuaTable.loadFile(fd):
            return
        if lc.instLuaTable.rownum() + 3 != sheet.nrows:
            print u'[%s::%s] 数据行数不致! xlsx[%s] lua[%s]' % (self.fdName, sheet.name, sheet.nrows - 3, lc.instLuaTable.rownum())
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
                luaval = lc.instLuaTable.get(vkey, keys[j])
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
            if fd in cfg.instCfg.luaFiles:
                if not self.compareLua(sheet, fd):
                    continue
            fd = sheet.name + '.csv'
            if fd in cfg.instCfg.csvFiles:
                rlt = self.compareCsv(sheet, fd)


instXlsxTable = XlsxTable()

def gao():
    for fd in cfg.instCfg.xlsxFiles:
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
        cfg.instCfg.load()
        cfg.instCfg.loadFiles()
        gao()
    except :
        print traceback.print_exc(5)

    set_color(FOREGROUND_DARKWHITE)
    raw_input('Done!')

