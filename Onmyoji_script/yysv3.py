#coding=utf-8
'''
Created on 2018/5/17 11:55:31

@author: tys
'''

import pykeyboard as pkb
import pymouse as pms
import time
import threading as trd
import os, sys
import random
import ctypes
import time
from win32gui import *
from win32api import GetSystemMetrics
import codecs
import traceback

class YYSKeyBoardEvent(pkb.PyKeyboardEvent):

    def __init__(self, master):
        pkb.PyKeyboardEvent.__init__(self)
        self.master = master

    def stop(self):
        pkb.PyKeyboardEvent.stop(self)
        self.master.escape()

class YYSMouseInvoker(pms.PyMouse):

    def __init__(self):
        pms.PyMouse.__init__(self)
        self.state = False
        self.startVal = 100
        self.interval = random.randint(20, 40) + 100

    def assign(self, posList, taskPosList):
        self.posList = posList[:]
        self.randPosList = posList[:]
        self.taskPosList = taskPosList[:]

    def setState(self, s):
        self.state = s

    def clickPos(self, pos):
        offsetX = random.randint(-20, 20)
        offsetY = random.randint(-5, 0)
        self.click(pos[0] + offsetX, pos[1] + offsetY, 1, random.randint(1, 2))

    def yysStart(self):
        self.state = True
        #ct: clieck type - 0为顺序点 非0为随机点 1.避免顺序点 点出了图层导致下一个的点击量不够 2.避免一直随机点点不到第二个窗口
        cnt, last, idx, ct = 0, 0, 0, 0
        nxt = 100
        ln = len(self.posList)

        taskNxt = 600
        taskIdx = 0
        taskCnt = 0

        screenWith = GetSystemMetrics(0)
        screenHeight = GetSystemMetrics(1)

        rdW, rdH = screenWith - 500, screenHeight - 100

        while True == self.state:
            time.sleep(0.025)
            cnt += 1
            taskCnt += 1
            if cnt >= nxt:
                if ct:
                    self.clickPos(self.randPosList[idx])
                else:
                    self.clickPos(self.posList[idx])
                idx += 1
                if idx >= ln:
                    cnt, idx = 0, 0
                    ct ^= 1
                    nxt = random.randint(80, 120)
                    random.shuffle(self.randPosList)
                else:
                    nxt += random.randint(10, 40)
            elif taskCnt >= taskNxt and taskIdx < len(self.taskPosList):
                self.clickPos(self.taskPosList[taskIdx])
                taskIdx += 1
                if taskIdx >= len(self.taskPosList):
                    taskCnt = 0
                    taskNxt = random.randint(500, 700)
                    taskIdx = 0
                else:
                    taskNxt += random.randint(50, 100)
            else:
                v = random.randint(1,100)
                if v < 2 and (last + 10 < cnt or last > cnt):
                    self.move(random.randint(20, rdW), random.randint(20, rdH))
                    last = cnt

class MainYYS(object):

    def __init__(self):
        self.stoper = YYSKeyBoardEvent(self)
        self.clicker = YYSMouseInvoker()
        self.state = False
        self.trdList = []
        self.posList = []
        self.dialogs = []
        self.taskPosList = []    # 协作坐标

    def waitting(self):
        self.state = True
        while True == self.state:
            time.sleep(0.02)
        self.clicker.setState(False)
        for t in self.trdList:
            t.join()

    def escape(self):
        self.state = False

    def startMouseControl(self):
        self.clicker.assign(self.posList, self.taskPosList)

        t = trd.Thread(target = self.stoper.run)
        t.setDaemon(True)
        self.trdList.append(t)
        t.start()

        t = trd.Thread(target = self.clicker.yysStart)
        t.setDaemon(True)
        self.trdList.append(t)
        t.start()

        self.waitting()

    def fixPositions(self, fixType):
        self.dialogs.sort()
        for i in xrange(0, len(self.dialogs)):
            lx, ly, rx, ry = self.dialogs[i]
            ltx, lty = rx - lx, ry - ly
            sx, sy = 0, 0
            ###########################################################
            #开始游戏位置
            if 1 == fixType:
                sx, sy = ltx * 74.1607 / 100 + lx, lty * 69.0068 / 100 + ly
            else:
                sx, sy = ltx * 81.3555 / 100 + lx, lty * 80.755 / 100 + ly
            self.posList.append((int(sx), int(sy)))
            ###########################################################
            #低部点击,两次
            self.posList.append((int((lx * 2 + rx) / 3.0), int(ry - 15)))
            self.posList.append((int((lx * 2 + rx) / 3.0), int(ry - 15)))
            ###########################################################
            #任务 只有组队才接，单人不接(不然会点到锁定)
            if 1 != fixType:
                tx, ty = ltx * 71.81 / 100 + lx, lty * 59.6 / 100 + ly
                self.taskPosList.append((int(tx), int(ty)))

    def start(self, fixType):
        self.listWindows()
        if len(self.dialogs) < 1:
            raise ValueError(u'未找到游戏窗口')
            return
        if len(self.dialogs) > 2:
            raise ValueError(u'游戏窗口过多(目前只支持1到2个)')
            return
        self.fixPositions(fixType)
        self.startMouseControl()

    def listWindows(self):
        self.dialogs = []
        tmp = '\xd2\xf5\xd1\xf4\xca\xa6'  #阴阳师
        def callback(hwnd, mouse):
            if IsWindow(hwnd) and IsWindowEnabled(hwnd) and IsWindowVisible(hwnd):
                title = GetWindowText(hwnd)
                if tmp in title:
                    self.dialogs.append(GetWindowRect(hwnd))
        EnumWindows(callback, 0)

instance = MainYYS()

def loadINI():
    showWindows = 0
    with open("cfg.ini", "r") as f:
        for line in f:
            if line.startswith("show"):
                a, b = line.split('=')
                showWindows = int(b.strip())
    return showWindows

def checkAdmin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def gao():
    try:
        args = sys.argv
        if len(args) < 2:
            raise ValueError(u'启动失败 args length ERROR! %s' % len(args))
            return
        if args[-1] not in ['1', '2']:
            raise ValueError(u'启动失败 args value ERROR! %s' % args[-1])
            return
        if not checkAdmin():
            ctypes.windll.shell32.ShellExecuteW(None, u'runas', unicode(sys.executable), unicode(__file__) + " " + args[-1], None, 1)
            return
        showWindows = 0
        # showWindows = loadINI()
        if showWindows > 0:
            pass
            # print u'按 <Enter> 键开始!!!'
            # raw_input()
        else:
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()    
            if not hwnd:
                raise ValueError(u'启动失败!!! 未知错误')
                return
            ctypes.windll.user32.ShowWindow(hwnd, 2)

        instance.start(int(args[-1]))

    except Exception, e:
        with codecs.open("error.log", "w", encoding = "GB2312") as of:
            print >> of, time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), unicode(e)


if __name__ == '__main__':
    gao()
    # os.system("timeout 3")
    # os.system("@pause")

