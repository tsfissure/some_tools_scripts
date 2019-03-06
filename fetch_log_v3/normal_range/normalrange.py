#coding=utf-8
'''
Created on 2018/10/22 10:51:00

@author: tys
'''

import sys,platform
if __name__ == '__main__':
    sys.path.append("../")

from fetchlog_common import basic as fb
import os
import openpyxl


class NormalRange(fb.FakerClient):

    def __init__(self):
        fb.FakerClient.__init__(self)
        self.svrranges = [(1, 230)]
        self.sql = ""

    def loadConfig(self):
        with open("normal_range.cfg", "r") as f:
            for line in f:
                if "servers" in line:
                    self.svrranges = []
                    ab = line[:-1].split('=')
                    if len(ab) != 2: continue
                    lst = ab[1].split(',')
                    for rg in lst:
                        lr = rg.split('-')
                        if len(lr) == 2:
                            self.svrranges.append((int(lr[0]), int(lr[1]) + 1))
                        elif len(lr) == 1:
                            self.svrranges.append((int(lr[0]), int(lr[0]) + 1))
                else:
                    self.sql += line[:-1] + " "

    def prepare(self):
        self.loadConfig()
        self.connectSSH()
        self.connectMySQL("frrsyslog")

    def gao(self):
        print self.svrranges
        xlsxName = "normalrange.xlsx"
        if os.path.exists(xlsxName):
            os.remove(xlsxName)
        book = openpyxl.Workbook()
        sheet = book.active
        for svrs in self.svrranges:
            l, r = svrs
            for i in xrange(l, r):
                sql = self.sql % i
                rows = self.execute(sql, ())
                print u'query:', i
                if len(rows) < 1:
                    print u'没有相应数据'
                else:
                    for row in rows:
                        sheet.append([i] + [unicode(j) for j in row])
        book.save(xlsxName)
        print u'数据已写入[%s]' % xlsxName


instance = NormalRange()

if __name__ == '__main__':
    instance.prepare()
    instance.gao()
    instance.close()
    raw_input(u'Done!')

