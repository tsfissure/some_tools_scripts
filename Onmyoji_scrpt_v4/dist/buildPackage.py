#coding=utf-8
'''
Created on 2019/6/11 17:55:39

@author: tsfissure
'''

import zipfile
import shutil
import os

fileList = ["使用教程.pdf", "鸡脚.exe"]

vl = 4
vr = int(input("版本号(一个整数)："))

fileName = "鸡脚_v%d_%d" % (vl, vr)
fileNameRar = fileName + ".rar"
imgPath = os.path.join(fileName, "img")

if os.path.exists(fileName) or os.path.exists(fileNameRar):
    msg = u'file[%s] or [%s] exists replase?(Y/N)' % (fileName, fileNameRar)
    rlt = 'a'
    while rlt.lower() not in ('y', 'n'):
        print(msg,)
        rlt = input()
    if rlt.lower() == 'n':
        print('Done')
        os.system("@pause")
        exit(0)
    print('recreate...')
if os.path.exists(fileNameRar):
    os.remove(fileNameRar)
if not os.path.exists(fileName):
    os.makedirs(fileName)
    os.makedirs(imgPath)

for fd in fileList:
    shutil.copy2(fd, fileName)

for root, dirs, files in os.walk("./img"):
    for fd in files:
        shutil.copy2(os.path.join(root, fd), imgPath)

with zipfile.ZipFile(fileNameRar, "w") as zfile:
    for root, dirs, files in os.walk(fileName):
        for fd in files:
            zfile.write(os.path.join(root, fd))

print('Done')
os.system("@pause")

if __name__ == '__main__':
    pass


