#coding=utf-8
'''
Created on 2019/6/6 9:58:31

@author: tsfissure
'''

import time, os, traceback
from pymouse import PyMouse
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from pynput import keyboard
import random
from win32api import GetSystemMetrics
import gameWindow

def WriteErrorLog():
    try:
        logPath = time.strftime("%Y/%m/%d")
        if not os.path.exists(logPath):
            os.makedirs(logPath)
        with open(os.path.join(logPath, time.strftime("%H.log")), "a") as of:
            print(time.strftime("[%Y-%m-%d %H:%M:%S]:"), file = of)
            traceback.print_exc(limit = 5, file = of)
    except:
        pass

class StopEventController(QThread):
    signalEvent = pyqtSignal()

    def __init__(self):
        super(StopEventController, self).__init__()

    def run(self):
        def on_press(key):
            if key == keyboard.Key.esc:
                self.signalEvent.emit()
                return False

        def on_release(key):
            if key == keyboard.Key.esc:
                return False

        with keyboard.Listener(on_press=on_press, on_release = on_release) as listener:
            listener.join()

class StopMouseController(QObject):
    signalEvent = pyqtSignal()

instStopMouseController = StopMouseController()

class MouseController(QThread):
    
    def __init__(self, hwndList, fightType, layer, period):
        super(MouseController, self).__init__()
        self.mRunning = False
        self.mGameWindows = []
        self.mPeriod = period
        hwndList.sort()
        try:
            for i in range(len(hwndList)):
                self.mGameWindows.append(gameWindow.GameWindow(hwndList[i][-1], i, fightType, layer))
        except:
            self.mGameWindows = []
            WriteErrorLog()
        self.mMouseCtrl = PyMouse()
        instStopMouseController.signalEvent.connect(self.OnStopEvent)

    def OnStopEvent(self):
        self.mRunning = False

    def run(self):
        screenWith = GetSystemMetrics(0)
        screenHeight = GetSystemMetrics(1)
        rdW, rdH = screenWith - 500, screenHeight - 100

        self.mRunning = True
        startTick = int(time.time())
        RAND_L = 0.3
        RAND_R = 1.0
        while self.mRunning:
            try:
                for i in range(len(self.mGameWindows)):
                    if i > 0: time.sleep(random.uniform(RAND_L, RAND_R))
                    if not self.mRunning: break
                    self.mGameWindows[i].Update()
                time.sleep(random.uniform(RAND_L, RAND_R))
                if not self.mRunning: break
                self.mMouseCtrl.move(random.randint(100, rdW), random.randint(100, rdH))
                time.sleep(random.uniform(RAND_L, RAND_R))
                now = int(time.time())
                if now - startTick >= self.mPeriod:
                    for window in self.mGameWindows:
                        window.KillSelf()
                    self.mGameWindows = []
                    break;
            except:
                WriteErrorLog()
                self.mGameWindows = []


if __name__ == '__main__':
    pass

