#coding=utf-8
'''
Created on 2019/6/5 20:20:45

@author: tsfissure
'''

import controller as ctrller
import sys, traceback, time, os
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextBrowser, QPushButton, QComboBox
from PyQt5.QtGui import QFont, QIcon
from win32gui import *
import win32api
import const
import ctypes

WINDOW_WIDTH    = 600
WINDOW_HEIGHT   = 200

POSX_DUP        = 30    # 副本按钮位置
POSX_THREE_TEAM = POSX_DUP + 100   # 三人副本按钮位置
POSX_TUPO       = POSX_THREE_TEAM + 100   # 突破
# POSX_TOWER_2    = 150   # 多人探索按钮位置
POSX_BOX        = WINDOW_WIDTH - 200    # 下拉列表位置
POSX_TOWER      = POSX_BOX + 70   # 探索按钮位置

class JiJioGUI(QMainWindow):

    def __init__(self):
        super().__init__()
        self.mRunning = False
        self.OnInit()
        self.OnInitUI()
        self.setFixedSize(self.width(), self.height())
        self.show()

    def OnInit(self):
        self.mStopThread = None
        self.mMouseThread = None
        self.mLastStopTick = 0

    def AddTextBrowser(self):
        self.textBrowser = QTextBrowser(self)
        self.textBrowser.resize(WINDOW_WIDTH - 60, WINDOW_HEIGHT - 70)
        self.textBrowser.move(30, 20)
        font = QFont("Courier New")
        font.setPointSize(8)
        self.textBrowser.setFont(font)

    def OnMessage(self, msg):
        self.textBrowser.append("[%s] %s" % (time.strftime("%H:%M:%S"), msg))
    
    def OnStopEvent(self):
        """监听到停止事件"""
        self.OnMessage("停止控制")
        ctrller.instStopMouseController.signalEvent.emit()
        self.mRunning = False
        self.mLastStopTick = int(time.time())

    def OnStart(self, fightType):
        try:
            if self.mRunning:
                self.OnMessage("正在进行控制，请先按<Esc>键停止控制")
                return
            if int(time.time()) - self.mLastStopTick < 5:
                self.OnMessage("失败! 请在3s后重试")
                return
            hwndList = []
            def callback(hwnd, mouse):
                if IsWindow(hwnd) and IsWindowEnabled(hwnd) and IsWindowVisible(hwnd):
                    title = GetWindowText(hwnd)
                    if const.NAME_WINDOW_TITLE in title:
                        rect = list(GetWindowRect(hwnd))
                        rect.append(hwnd)
                        hwndList.append(rect)
            EnumWindows(callback, 0)
            if len(hwndList) < 1:
                self.OnMessage("未找到游戏窗口,请先打开游戏到特定界面")
                return
            if len(hwndList) > 3:
                self.OnMessage("游戏窗口过多,目前最多三个")
                return
            layer = self.mTowerDropList[self.mTowerDropBox.currentIndex()] if fightType == const.FIGHT_TYPE_TANSUO and 1 == len(hwndList) else 0 #探索的章节
            if self.mStopThread: self.mStopThread = None
            self.mStopThread = ctrller.StopEventController()
            self.mStopThread.signalEvent.connect(self.OnStopEvent)
            self.mStopThread.start()
            if self.mMouseThread: self.mMouseThread = None
            self.mMouseThread = ctrller.MouseController(hwndList, fightType, layer)
            self.mMouseThread.start()
            self.mRunning = True
            self.OnMessage("开始控制")
        except:
            ctrller.WriteErrorLog()
            self.OnMessage("执行出错,请查看日志")

    def AddDuplicateButton(self):
        self.mDupBtn = QPushButton("单双人本", self)
        self.mDupBtn.move(POSX_DUP, WINDOW_HEIGHT - 40)
        self.mDupBtn.clicked.connect(lambda : self.OnStart(const.FIGHT_TYPE_DUPLICATE))

    def AddTowerButton(self):
        self.mTowerBtn = QPushButton("探索", self)
        self.mTowerBtn.move(POSX_TOWER, WINDOW_HEIGHT - 40)
        self.mTowerBtn.clicked.connect(lambda : self.OnStart(const.FIGHT_TYPE_TANSUO))

    def AddTowerDoubleButton(self):
        self.mTowerDoubleBtn = QPushButton("多人探索", self)
        self.mTowerBtn.move(POSX_TOWER_2, WINDOW_HEIGHT - 40)
        self.mTowerBtn.clicked.connect(lambda : self.OnStart(const.FIGHT_TYPE_TANSUO_DOUBLE))

    def AddTowerDropList(self):
        """探索章节下拉框"""
        self.mTowerDropList = [i for i in range(1, 40) if os.path.exists("img/ts%d.png" % i)]
        if 0 == len(self.mTowerDropList): return
        self.mTowerDropList.reverse()
        self.mTowerDropBox = QComboBox(self)
        self.mTowerDropBox.addItems(["第%d章" % i for i in self.mTowerDropList])
        self.mTowerDropBox.resize(65, self.mTowerBtn.size().height())
        self.mTowerDropBox.move(POSX_BOX, WINDOW_HEIGHT - 40)
        self.mTowerDropBox.currentIndexChanged.connect(lambda index: self.OnMessage("已选择:探索第%d章(单人探索生效)" % self.mTowerDropList[index]))

    def AddThreeTream(self):
        """三人队伍按钮"""
        self.mThreeBtn = QPushButton("三人副本", self)
        self.mThreeBtn.move(POSX_THREE_TEAM, WINDOW_HEIGHT - 40)
        self.mThreeBtn.clicked.connect(lambda : self.OnStart(const.FIGHT_TYPE_THREE_TEAM))

    def AddTupoButton(self):
        """突破"""
        self.mTupoBtn = QPushButton("突破", self)
        self.mTupoBtn.move(POSX_TUPO, WINDOW_HEIGHT - 40)
        self.mTupoBtn.clicked.connect(lambda : self.OnStart(const.FIGHT_TYPE_TUPO))

    def OnInitUI(self):
        self.AddTextBrowser()
        self.AddDuplicateButton()
        self.AddTowerButton()
        # self.AddTowerDoubleButton()
        self.AddTowerDropList()
        self.AddThreeTream()
        self.AddTupoButton()

        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setWindowIcon(QIcon('img/fav.ico'))
        self.OnMessage("初始化成功")
        self.OnMessage("副本包括(御魂,觉醒,业原火,御灵)")
        if len(self.mTowerDropList) > 0:
            self.OnMessage("已选择:探索第%d章(单人探索生效)" % self.mTowerDropList[self.mTowerDropBox.currentIndex()])

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("鸡jio v4.2")
    try:
        window = JiJioGUI()
    except:
        ctrller.WriteErrorLog()
        exit(0)
    sys.exit(app.exec_())

if __name__ == '__main__':
    if len(sys.argv) < 2:
        try:
            if not ctypes.windll.shell32.IsUserAnAdmin():
                win32api.ShellExecute(None, u'runas', sys.executable, __file__, None, 1)
                sys.exit(0)
        except:
            sys.exit(0)
    main()

