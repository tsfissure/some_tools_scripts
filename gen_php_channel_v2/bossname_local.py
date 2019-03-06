#coding=utf-8
'''
Created on 2019/1/21 11:03:20

@author: tys
'''

import os
import traceback
import csv
import codecs

CFG_PATH = "E:/fanren_branches_360/data/zh_CN/data"

class BossNameLocal(object):

    def __init__(self):
        self.nameLst = {}
        self.mondef = {}

    def assign(self, monsterId):
        name = self.mondef.get(monsterId, "Unknown")
        self.nameLst[monsterId] = name

    def csvLoader(self, csvName, idx = None):
        print 'loading %s' % csvName
        fd = os.path.join(CFG_PATH, csvName)
        with open(fd, "r") as f:
            reader = csv.reader(f)
            rowNum = 0
            for row in reader:
                rowNum += 1
                if rowNum < 4: continue
                if idx:
                    self.assign(int(row[idx]))
                else:
                    self.mondef[int(row[0])] = row[2]

    def output(self):
        print 'output'
        with codecs.open("bossname.php", "w", "utf-8") as of:
            header = "<?php\nreturn ["
            footer = "]"
            print >> of, header
            for k, v in self.nameLst.iteritems():
                of.write("\t'%s'=>'%s',\n" % (k, v.decode('gb2312')))
            print >> of, footer

    def execute(self):
        self.csvLoader("mondef.csv")
        self.csvLoader("sanctuaryBossTable.csv", 1)
        self.csvLoader("elementBossTable.csv", 2)
        self.csvLoader("eliteBossTable.csv", 2)
        self.csvLoader("yaojieBossTable.csv", 2)
        self.csvLoader("bfkhYjrqTable.csv", 2)
        self.csvLoader("worldBossTable.csv", 1)
        self.csvLoader("skyBossTable.csv", 5)
        self.output()

instance = BossNameLocal()

if __name__ == '__main__':
    try:
        instance.execute()
    except Exception, e:
        traceback.print_exc(limit = 5)
    raw_input('Done!')


