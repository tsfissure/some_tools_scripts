#coding=utf-8
'''
Created on 2019/6/5 16:40:34

@author: tsfissure
'''

import controller as ctrller
import const
import os, random
import traceback
from win32gui import GetWindowRect, GetWindowDC, ReleaseDC, DeleteObject, SetForegroundWindow
from win32ui import CreateDCFromHandle, CreateBitmap
from win32con import FILE_ATTRIBUTE_HIDDEN, SRCCOPY
from win32api import SetFileAttributes
from win32process import GetWindowThreadProcessId
import aircv
import cv2
from pymouse import PyMouse
# from PIL import ImageGrab
import time
import psutil

POSITION_RANDOM_LEFT    = -30
POSITION_RANDOM_RIGHT   = 30
POSITION_RANDOM_UP      = -10
POSITION_RANDOM_DOWN    = 10


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
        self.mMouseCtrl = PyMouse()
        self.OnInit()
        self.InitPoints()
        self.LoadImages()
        self.mTansuoMoveCnt = 0
        self.mErrorCount = 0

    def OnInit(self):
        self.mPath = "tmpFiles/%d/" % self.mWindowOrder #主要存储路径
        if not os.path.exists(self.mPath):
            os.makedirs(self.mPath)
            SetFileAttributes("tmpFiles", FILE_ATTRIBUTE_HIDDEN)
        self.mScreenShotFileName = os.path.join(self.mPath, const.NAME_SCREEN_SHOT)

    def InitPoints(self):
        """ 计算一些常量坐标 """
        rect = GetWindowRect(self.mHwnd)
        self.mHwndRect = rect
        self.mUseSystemScreenShot = rect[0] > 2000 # 多屏
        self.mHwndLeftUpX, self.mHwndLeftUpY = rect[:2] # 窗口左上角坐标
        height, width = rect[3] - rect[1], rect[2] - rect[0]
        self.mWindowHeight = height; self.mWindowWidth = width # 窗口宽和高
        self.mTSLeftMovePos = (int(self.mHwndLeftUpX + 100), int(self.mHwndLeftUpY + self.mWindowHeight * 3.0 / 4)) # 探索左移坐标
        self.mTSRightMovePos = (int(self.mHwndLeftUpX + self.mWindowWidth - 100), int(self.mHwndLeftUpY + self.mWindowHeight * 3.0 / 4)) # 探索右移坐标
        # 没有操作时的点击,预防奖励把屏幕占满找不到可点的)和省掉很多需要判断点击的界面
        if self.mFightType == const.FIGHT_TYPE_TUPO:
            self.mNoOperatePos = (int(self.mHwndLeftUpX + width * 0.2), int(self.mHwndLeftUpY + height * 0.76))
            self.mTupoResetPos = (int(self.mHwndLeftUpX + 50), int(self.mHwndLeftUpY + height * 0.5))
            self.mTupoType = const.TUPO_TYPE_UNKNOWN
            self.mTupoReset = False
            self.mCantGuidTupo = False # 能不能打寮突破
            self.mCantPersonTupo = False # 能不能打个突
            self.mNextAttackTick = 0 # 寮突没有可打次数等待时间
        else:
            self.mNoOperatePos = (int((self.mHwndLeftUpX * 2 + rect[2]) / 3.0), int(rect[3] - 20))
        # # 探索的时候如果在主界面，需要滚动，利用这个坐标滚动动
        # self.mTowerPos = (int(self.mHwndLeftUpX + width * 0.88), int(self.mHwndLeftUpY + height * 0.5))

    def LoadImageInternal(self, name):
        """
        LoadImages common
        resize是因为游戏窗口会被玩家缩放
        """
        img = cv2.imread(os.path.join("img/", name))
        H, W = img.shape[:2]
        newSize = (int(self.mWindowWidth * W / 1152), int(self.mWindowHeight * H / 678))
        newImg = cv2.resize(img, newSize, interpolation = cv2.INTER_AREA)
        # cv2.imwrite(os.path.join(self.mPath, name), newImg)
        return newImg

    def LoadImages(self):
        """
        把默认比例的图片经过resize后存到tmp/xx/目录下
        再分类(要点击的，要判断的，先存起来)
        """
        self.mClickImages = []
        if self.mFightType == const.FIGHT_TYPE_DUPLICATE or self.mFightType == const.FIGHT_TYPE_THREE_TEAM: # 自动接受要是接受前面
            self.mClickImages.append(self.LoadImageInternal(const.NAME_AUTO_ACCETP))    # 接受协作要很优先
        self.mTaskImg = self.LoadImageInternal(const.NAME_TASK)
        self.mClickImages.append(self.mTaskImg)
        if self.mFightType == const.FIGHT_TYPE_DUPLICATE: #副本
            self.mClickImages.append(self.LoadImageInternal(const.NAME_CHALLENGE))
            self.mClickImages.append(self.LoadImageInternal(const.NAME_DUP_FIGHT))
            self.mClickImages.append(self.LoadImageInternal(const.NAME_AUTO_INVITE))
        elif self.mFightType == const.FIGHT_TYPE_TANSUO: #探索
            self.mClickImages.append(self.LoadImageInternal(const.NAME_TANSUO_BOX))
            if 0 == self.mWindowOrder: # 司机
                self.mClickImages.append(self.LoadImageInternal(const.NAME_TANSUO))
                self.mClickImages.append(self.LoadImageInternal(const.NAME_TANSUO_BOSS))
                self.mClickImages.append(self.LoadImageInternal(const.NAME_TANSUO_FIGHT))
                self.mClickImages.append(self.LoadImageInternal(const.NAME_INVITE))
                self.mTowerMainSceneImg = self.LoadImageInternal(const.NAME_TANSUO_MAIN) #探索主场景
            if self.mLayer > 0:
                self.mClickImages.append(self.LoadImageInternal("ts%d.png" % self.mLayer))
        elif self.mFightType == const.FIGHT_TYPE_THREE_TEAM: # 三人队
            self.mThreeTeamFight = self.LoadImageInternal(const.NAME_DUP_FIGHT)
            self.mThreeTeamInvite = self.LoadImageInternal(const.NAME_THREE_INVITE)
            self.mClickImages.append(self.LoadImageInternal(const.NAME_AUTO_INVITE))
        elif self.mFightType == const.FIGHT_TYPE_TUPO: # 突破
            self.mTupoAttack = self.LoadImageInternal(const.NAME_ATTCK)
            self.mTupoRecord = self.LoadImageInternal(const.NAME_TUPO_REC)
            self.mGuildTupo = self.LoadImageInternal(const.NAME_GUILD_TUPO)
            self.mClickImages.append(self.mTupoAttack)
            for i in range(5, -1, -1):
                self.mClickImages.append(self.LoadImageInternal("tp%d.png" % i))
            # self.mClickImages.append(self.LoadImageInternal(const.NAME_REFRESH))
            self.mLockImg = self.LoadImageInternal(const.NAME_LOCK)
            self.mClickImages.append(self.LoadImageInternal(const.NAME_TUPO_BTN))
            self.mCantGuildTupoImg = self.LoadImageInternal(const.NAME_CANT_GUILD_TUPO)
            self.mCantPersonTupoImg = self.LoadImageInternal(const.NAME_CANT_PERSON_TUPO)
        elif self.mFightType == const.FIGHT_TYPE_TUZIJING:
            self.mClickImages.append(self.LoadImageInternal(const.NAME_TUZIJING))
            self.mClickImages.append(self.LoadImageInternal(const.NAME_DUP_FIGHT))
            self.mClickImages.append(self.LoadImageInternal(const.NAME_AUTO_INVITE))
        self.mClickImages.append(self.LoadImageInternal(const.NAME_READY_BTN))
        self.mClickImages.append(self.LoadImageInternal(const.NAME_CONFIRM))
        self.mClickImages.append(self.LoadImageInternal(const.NAME_ACCEPT))

    def ScreenShot(self):
        """
        截图 网上找的代码直接复制修改的
        后面加了释放资源代码，网上找的
        """
        hwndDC = GetWindowDC(self.mHwnd)
        mfcDC = CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()
        saveBitMap = CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, self.mWindowWidth, self.mWindowHeight)
        saveDC.SelectObject(saveBitMap)
        saveDC.BitBlt((0, 0), (self.mWindowWidth, self.mWindowHeight), mfcDC, (0, 0), SRCCOPY)
        saveBitMap.SaveBitmapFile(saveDC, self.mScreenShotFileName)
        self.mImageSrc = aircv.imread(self.mScreenShotFileName)
        # release 
        DeleteObject(saveBitMap.GetHandle())
        mfcDC.DeleteDC()
        saveDC.DeleteDC()
        ReleaseDC(self.mHwnd, hwndDC)

    def ScreenShotPIL(self):
        im = ImageGrab.grab(self.mHwndRect)
        im.save(self.mScreenShotFileName)
        self.mImageSrc = aircv.imread(self.mScreenShotFileName)

    def TryMouseClick(self, X, Y):
        self.mMouseCtrl.click(X, Y, random.randint(1, 2))

    def TryMouseClickPos(self, pos):
        X = int(pos[0] + random.randint(POSITION_RANDOM_LEFT, POSITION_RANDOM_RIGHT))
        Y = int(pos[1] + random.randint(POSITION_RANDOM_UP, POSITION_RANDOM_DOWN))
        self.TryMouseClick(X, Y)

    def TryClick(self, imgSch):
        """
        尝试点击，判断成功点击返回True
        """
        rlt = aircv.find_template(self.mImageSrc, imgSch)
        # rlt = aircv.find_template(self.mImageSrc, aircv.imread(os.path.join(self.mPath, imgName)))
        if not rlt: return False
        confidence = rlt["confidence"]
        if confidence >= 0.9:
            # print("click", imgSch, self.mWindowOrder, confidence)
            pos = rlt["result"]
            X = int(pos[0] + self.mHwndLeftUpX + random.randint(POSITION_RANDOM_LEFT, POSITION_RANDOM_RIGHT))
            Y = int(pos[1] + self.mHwndLeftUpY + random.randint(POSITION_RANDOM_UP, POSITION_RANDOM_DOWN))
            self.TryMouseClick(X, Y)
            return True
        return False

    def CheckImageExists(self, imgSch, click = const.CHECK_CLICK_TYPE_NONE):
        rlt = aircv.find_template(self.mImageSrc, imgSch)
        if not rlt: return False
        if rlt["confidence"] >= 0.9:
            if click == const.CHECK_CLICK_TYPE_UP:
                rect = rlt["rectangle"]
                X = int(rect[0][0] + self.mHwndLeftUpX + random.randint(POSITION_RANDOM_LEFT, POSITION_RANDOM_RIGHT))
                Y = int(rect[0][1] - 20 + self.mHwndLeftUpY + random.randint(POSITION_RANDOM_UP, POSITION_RANDOM_DOWN))
                self.TryMouseClick(X, Y)
            elif click == const.CHECK_CLICK_TYPE_CENTER:
                pos = rlt["result"]
                X = int(pos[0] + self.mHwndLeftUpX + random.randint(POSITION_RANDOM_LEFT, POSITION_RANDOM_RIGHT))
                Y = int(pos[1] + self.mHwndLeftUpY + random.randint(POSITION_RANDOM_UP, POSITION_RANDOM_DOWN))
                self.TryMouseClick(X, Y)
            return True
        return False

    def UpdateTupo(self):
        """突破比较特殊处理"""
        if self.mFightType != const.FIGHT_TYPE_TUPO: return False
        if self.mTupoReset:
            self.mTupoReset = False
            self.TryMouseClickPos(self.mTupoResetPos)
            return True

        if self.mTupoType == const.TUPO_TYPE_UNKNOWN:
            if self.CheckImageExists(self.mTupoRecord):
                self.mTupoType = const.TUPO_TYPE_GUILD
            else:
                self.mTupoType = const.TUPO_TYPE_PERSON
        if self.mTupoType == const.TUPO_TYPE_GUILD:
            if self.TryClick(self.mGuildTupo):
                return True
            if self.CheckImageExists(self.mTupoAttack) and random.randint(1, 5) == 1: # 五分之一的概率回到界面重新获得新的寮突数据
                self.mTupoReset = True
                self.TryMouseClickPos(self.mNoOperatePos)
                return True
        return False

    def UpdateCantTupo(self): # 等待突破(没次数了就不用一直点点点)
        if self.mFightType != const.FIGHT_TYPE_TUPO: return False
        if self.mTupoType == const.TUPO_TYPE_GUILD:
            now = int(time.time())
            if self.mCantGuidTupo and now >= self.mNextAttackTick:
                self.mCantGuidTupo = False
            if not self.mCantGuidTupo and self.CheckImageExists(self.mCantGuildTupoImg):
                    self.mNextAttackTick = now + 30 # 等待半分钟
                    self.mCantGuidTupo = True
            return self.mCantGuidTupo
        elif self.mTupoType == const.TUPO_TYPE_PERSON:
            if not self.mCantPersonTupo and self.CheckImageExists(self.mCantPersonTupoImg):
                self.mCantPersonTupo = True
            return False #self.mCantPersonTupo
        return False

    def KillSelf(self):
        _, PID = GetWindowThreadProcessId(self.mHwnd)
        p = psutil.Process(PID)
        p.terminate()

    def Update(self):
        if self.mErrorCount >= 100: return
        try:
            # SetForegroundWindow(self.mHwnd)
            # if self.mUseSystemScreenShot:
            #     self.ScreenShot()
            # else:
            #     self.ScreenShotPIL()
            self.ScreenShot()
            if self.UpdateTupo() or self.UpdateCantTupo():
                self.TryClick(self.mTaskImg)
                return
            for img in self.mClickImages:
                if self.TryClick(img):
                    self.mTansuoMoveCnt = 0
                    break
            else:
                if self.mFightType == const.FIGHT_TYPE_TANSUO:
                    if 0 == self.mWindowOrder and self.CheckImageExists(self.mTowerMainSceneImg): #探索的时候在主界面，移动
                        # print("探索主界面", self.mWindowOrder)
                        self.mTansuoMoveCnt += 1
                        if 1 == (int(self.mTansuoMoveCnt / 8) & 1):
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
                elif self.mFightType == const.FIGHT_TYPE_DUPLICATE or self.mFightType == const.FIGHT_TYPE_TUZIJING:
                    # print("界面左下方", self.mWindowOrder)
                    self.TryMouseClickPos(self.mNoOperatePos)
                elif self.mFightType == const.FIGHT_TYPE_THREE_TEAM:
                    # 在组队界面不需要操作, 直到没有"邀请"
                    if not self.CheckImageExists(self.mThreeTeamInvite) and not self.CheckImageExists(self.mThreeTeamFight, const.CHECK_CLICK_TYPE_CENTER):
                        self.TryMouseClickPos(self.mNoOperatePos)
                elif self.mFightType == const.FIGHT_TYPE_TUPO:
                    if not self.CheckImageExists(self.mLockImg):
                        self.TryMouseClickPos(self.mNoOperatePos)
        except:
            ctrller.WriteErrorLog()
            self.mErrorCount += 1

# instance = GameWindow(0, 1)

if __name__ == '__main__':
    pass
    # while True:
    #     x = eval(input('input:'))
    #     if 0 == x:
    #         break
    #     else:
    #         try:
    #             instance.ScreenShot()
    #         except:
    #             traceback.print_exc(5)


