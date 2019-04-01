#coding=utf-8
'''
Created on 2019/4/1 11:36:32

@author: tys
'''

import os


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

