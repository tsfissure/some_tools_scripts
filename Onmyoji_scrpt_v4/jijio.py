#coding=utf-8
'''
Created on 2019/6/5 20:20:45

@author: tsfissure
'''

import sys, traceback, time
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextBrowser, QPushButton
from PyQt5.QtGui import QFont, QIcon
from win32gui import *
import win32api
import const
import controller as ctrller
import ctypes

WINDOW_WIDTH    = 500
WINDOW_HEIGHT   = 200

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
        if self.mRunning:
            self.OnMessage("正在进行控制，请先按<Esc>键停止控制")
            return
        if int(time.time()) - self.mLastStopTick < 5:
            self.OnMessage("失败! 请在3s后重试")
            return
        hwndList = []
        yysTitle = "阴阳师"
        def callback(hwnd, mouse):
            if IsWindow(hwnd) and IsWindowEnabled(hwnd) and IsWindowVisible(hwnd):
                title = GetWindowText(hwnd)
                if yysTitle in title:
                    rect = list(GetWindowRect(hwnd))
                    rect.append(hwnd)
                    hwndList.append(rect)
        EnumWindows(callback, 0)
        if len(hwndList) < 1:
            self.OnMessage("未找到游戏窗口,请先打开游戏到特定界面")
            return
        if len(hwndList) > 2:
            self.OnMessage("游戏窗口过多")
            return
        if self.mStopThread: self.mStopThread = None
        self.mStopThread = ctrller.StopEventController()
        self.mStopThread.signalEvent.connect(self.OnStopEvent)
        self.mStopThread.start()
        if self.mMouseThread: self.mMouseThread = None
        self.mMouseThread = ctrller.MouseController(hwndList, fightType)
        self.mMouseThread.start()
        self.mRunning = True
        self.OnMessage("开始控制")

    def AddDuplicateButton(self):
        self.mDupBtn = QPushButton("副本", self)
        self.mDupBtn.move(100, WINDOW_HEIGHT - 40)
        self.mDupBtn.clicked.connect(lambda : self.OnStart(const.FIGHT_TYPE_DUPLICATE))

    def AddTowerButton(self):
        self.mTowerBtn = QPushButton("探索", self)
        self.mTowerBtn.move(300, WINDOW_HEIGHT - 40)
        self.mTowerBtn.clicked.connect(lambda : self.OnStart(const.FIGHT_TYPE_TANSUO))

    def OnInitUI(self):
        self.AddTextBrowser()
        self.AddDuplicateButton()
        self.AddTowerButton()

        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setWindowIcon(QIcon('img/fav.ico'))
        self.OnMessage("初始化成功")

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("鸡jio v4.0")
    try:
        window = JiJioGUI()
    except:
        traceback.print_exc(5)
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

