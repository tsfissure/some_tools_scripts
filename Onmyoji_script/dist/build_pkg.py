#coding=utf-8
'''
Created on 2018/5/21 13:49:58

@author: tys
'''

import zipfile
import shutil
import os

fileList = ["document.pdf", "update.log", "yysv3.exe", u"单刷.bat", u"组队.bat"]

print u'Please input versin number(two integers):',
vl, vr = map(int, raw_input().split(' '))

fileName = "omj_v%d_%d" % (vl, vr)
fileNameRar = fileName + ".rar"

if os.path.exists(fileName) or os.path.exists(fileNameRar):
    msg = u'file[%s] or [%s] exists replase?(Y/N)' % (fileName, fileNameRar)
    # print msg,
    rlt = 'a'
    while rlt.lower() not in ('y', 'n'):
        print msg,
        rlt = raw_input()
    if rlt.lower() == 'n':
        print u'Done'
        os.system("@pause")
        exit(0)
    print u'recreate...'
    # os.removedirs(fileName)
if os.path.exists(fileNameRar):
    os.remove(fileNameRar)
if not os.path.exists(fileName):
    os.makedirs(fileName)


for fd in fileList:
    shutil.copy2(fd, fileName)

with zipfile.ZipFile(fileNameRar, "w") as zfile:
    for f in fileList:
        fd = fileName + "/" + f
        zfile.write(fd)

print u'Done'
os.system("@pause")

if __name__ == '__main__':
    pass

