#coding=utf-8
'''
Created on 2019/6/5 16:40:34

@author: tsfissure
'''

import controller as ctrller
import const
import os, random
import traceback
import win32gui, win32ui, win32con, win32api
import aircv
import cv2
import pymouse

class GameWindow(object):
    def __init__(self, hwnd, windowOrder, fightType, layer = 0):
        """
        hwnd：游戏窗口句柄
        windowOrder: 游戏窗口序号
        fightType: 副本/探索
        layer: 第layer章探索(单人生效)
        """
        self.mHwnd = hwnd
        self.mWindowOrder = windowOrder # 窗口顺序,探索组队时司机要在左边(order为0)
        self.mFightType = fightType
        self.mLayer = layer
        self.mMouseCtrl = pymouse.PyMouse()
        self.OnInit()
        self.InitPoints()
        self.LoadImages()
        self.InitClickImages()
        self.mTansuoMoveCnt = 0

    def OnInit(self):
        self.mPath = "tmpFiles/%d/" % self.mWindowOrder #主要存储路径
        if not os.path.exists(self.mPath):
            os.makedirs(self.mPath)
            win32api.SetFileAttributes("tmpFiles", win32con.FILE_ATTRIBUTE_HIDDEN)
        self.mScreenShotFileName = os.path.join(self.mPath, const.NAME_SCREEN_SHOT)

    def InitClickImages(self):
        self.mClickImages = []
        if self.mFightType == const.FIGHT_TYPE_DUPLICATE:
            self.mClickImages.append(const.NAME_CHALLENGE)
            self.mClickImages.append(const.NAME_DUP_FIGHT)
            self.mClickImages.append(const.NAME_AUTO_INVITE)
            self.mClickImages.append(const.NAME_AUTO_ACCETP)
        else:
            self.mClickImages.append(const.NAME_TANSUO_BOX)
            if 0 == self.mWindowOrder: # 司机
            # if self.mFightType != const.FIGHT_TYPE_TANSUO_DOUBLE or 0 == self.mWindowOrder: # 司机
                self.mClickImages.append(const.NAME_TANSUO)
                self.mClickImages.append(const.NAME_TANSUO_BOSS)
                self.mClickImages.append(const.NAME_TANSUO_FIGHT)
                self.mClickImages.append(const.NAME_INVITE)
            if self.mLayer > 0:
                self.mClickImages.append("ts%s.png" % self.mLayer)
        self.mClickImages.append(const.NAME_TASK)
        self.mClickImages.append(const.NAME_READY_BTN)
        self.mClickImages.append(const.NAME_CONFIRM)
        self.mClickImages.append(const.NAME_ACCEPT)

    def InitPoints(self):
        """ 计算一些常量坐标 """
        rect = win32gui.GetWindowRect(self.mHwnd)
        self.mHwndLeftUpX, self.mHwndLeftUpY = rect[:2] # 窗口左上角坐标
        height, width = rect[3] - rect[1], rect[2] - rect[0]
        self.mWindowHeight = height; self.mWindowWidth = width # 窗口宽和高
        self.mTSLeftMovePos = (int(self.mHwndLeftUpX + 100), int(self.mHwndLeftUpY + self.mWindowHeight * 3.0 / 4)) # 探索左移坐标
        self.mTSRightMovePos = (int(self.mHwndLeftUpX + self.mWindowWidth - 100), int(self.mHwndLeftUpY + self.mWindowHeight * 3.0 / 4)) # 探索右移坐标
        # 没有操作时的点击,预防奖励把屏幕占满找不到可点的)
        self.mNoOperatePos = (int(self.mHwndLeftUpX + 100), int(self.mWindowHeight * 0.82))
        # # 探索的时候如果在主界面，需要滚动，利用这个坐标滚动动
        # self.mTowerPos = (int(self.mHwndLeftUpX + width * 0.88), int(self.mHwndLeftUpY + height * 0.5))

    def LoadImageInternal(self, name):
        """ LoadImages common """
        img = cv2.imread(os.path.join("img/", name))
        H, W = img.shape[:2]
        newSize = (int(self.mWindowWidth * W / 1152), int(self.mWindowHeight * H / 679))
        newImg = cv2.resize(img, newSize, interpolation = cv2.INTER_AREA)
        cv2.imwrite(os.path.join(self.mPath, name), newImg)

    def LoadImages(self):
        """
        把默认比例的图片经过resize后存到tmp/xx/目录下
        resize是因为游戏窗口会被玩家缩放
        """
        self.LoadImageInternal(const.NAME_TASK)
        self.LoadImageInternal(const.NAME_ACCEPT)
        self.LoadImageInternal(const.NAME_CONFIRM)
        self.LoadImageInternal(const.NAME_READY_BTN)
        if self.mFightType == const.FIGHT_TYPE_DUPLICATE:
            self.LoadImageInternal(const.NAME_AUTO_INVITE)
            self.LoadImageInternal(const.NAME_AUTO_ACCETP)
            self.LoadImageInternal(const.NAME_CHALLENGE)
            self.LoadImageInternal(const.NAME_DUP_FIGHT)
        else:
            self.LoadImageInternal(const.NAME_TANSUO_BOX)
            # if self.mFightType != const.FIGHT_TYPE_TANSUO_DOUBLE or 0 == self.mWindowOrder: # 司机
            if 0 == self.mWindowOrder: # 司机
                self.LoadImageInternal(const.NAME_TANSUO)
                self.LoadImageInternal(const.NAME_TANSUO_FIGHT)
                self.LoadImageInternal(const.NAME_TANSUO_MAIN)
                self.LoadImageInternal(const.NAME_TANSUO_BOSS)
                self.LoadImageInternal(const.NAME_INVITE)
                # self.LoadImageInternal(const.NAME_YUHUN_BTN)
            if self.mLayer > 0:
                self.LoadImageInternal("ts%d.png" % self.mLayer)

    def ScreenShot(self):
        """ 截图 网上找的代码直接复制修改的 """
        hwndDC = win32gui.GetWindowDC(self.mHwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()
        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, self.mWindowWidth, self.mWindowHeight)
        saveDC.SelectObject(saveBitMap)
        saveDC.BitBlt((0, 0), (self.mWindowWidth, self.mWindowHeight), mfcDC, (0, 0), win32con.SRCCOPY)
        saveBitMap.SaveBitmapFile(saveDC, self.mScreenShotFileName)
        self.mImageSrc = aircv.imread(self.mScreenShotFileName)

    def TryMouseClick(self, X, Y):
        self.mMouseCtrl.click(X, Y, random.randint(1, 2))

    def TryMouseClickPos(self, pos):
        self.TryMouseClick(pos[0], pos[1])

    def TryClick(self, imgName):
        """
        尝试点击，判断成功点击返回True
        """
        rlt = aircv.find_template(self.mImageSrc, aircv.imread(os.path.join(self.mPath, imgName)))
        if not rlt: return False
        confidence = rlt["confidence"]
        if confidence >= 0.9:
            # print("click", imgName, self.mWindowOrder, confidence)
            pos = rlt["result"]
            X = int(pos[0] + self.mHwndLeftUpX + random.randint(-10, 10))
            Y = int(pos[1] + self.mHwndLeftUpY + random.randint(-5, 5))
            self.TryMouseClick(X, Y)
            return True
        return False

    def CheckImageExists(self, imgName, click = False):
        rlt = aircv.find_template(self.mImageSrc, aircv.imread(os.path.join(self.mPath, imgName)))
        if not rlt: return False
        if rlt["confidence"] >= 0.9:
            if click:
                rect = rlt["rectangle"]
                X = int(rect[0][0] + self.mHwndLeftUpX + random.randint(-10, 10))
                Y = int(rect[0][1] - 20 + self.mHwndLeftUpY + random.randint(-5, 5))
                self.TryMouseClick(X, Y)
            return True
        return False

    def Update(self):
        self.ScreenShot()
        try:
            for img in self.mClickImages:
                if self.TryClick(img):
                    self.mTansuoMoveCnt = 0
                    break
            else:
                if self.mFightType == const.FIGHT_TYPE_TANSUO:
                    if 0 == self.mWindowOrder and self.CheckImageExists(const.NAME_TANSUO_MAIN): #探索的时候在主界面，移动
                        # print("探索主界面", self.mWindowOrder)
                        self.mTansuoMoveCnt += 1
                        if 1 == (int(self.mTansuoMoveCnt / 5) & 1):
                            self.TryMouseClickPos(self.mTSLeftMovePos)
                        else:
                            self.TryMouseClickPos(self.mTSRightMovePos)
                    # elif self.mLayer > 0 and self.CheckImageExists(const.NAME_YUHUN_BTN): # 需要滚动右边的探索章节
                    #     self.mMouseCtrl.move(self.mTowerPos[0], self.mTowerPos[1])
                    #     self.mMouseCtrl.scroll(4)
                    #     print("滚动")
                    else:
                        # print("左下方", self.mWindowOrder)
                        self.TryMouseClickPos(self.mNoOperatePos)
                elif self.mFightType == const.FIGHT_TYPE_DUPLICATE:
                    # print("界面左下方", self.mWindowOrder)
                    self.TryMouseClickPos(self.mNoOperatePos)
        except:
            ctrller.WriteErrorLog()

# instance = GameWindow(0, 1)

if __name__ == '__main__':
    while True:
        x = eval(input('input:'))
        if 0 == x:
            break
        else:
            try:
                instance.ScreenShot()
            except:
                traceback.print_exc(5)


