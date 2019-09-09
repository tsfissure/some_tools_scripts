#coding=utf-8
'''
Created on 2019/5/28 17:01:22

@author: tys
'''

import sys, os, json, time
import pandas, xlrd
from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QTextBrowser, QPushButton,
        QGridLayout, QFileDialog)
from PyQt5.QtGui import QIcon, QFont, QTextCursor
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import traceback

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 500

class ConfigParam(object):

    def __init__(self):
        self.cfgs = {}

    def load(self):
        if not os.path.exists("config.cfg"):
            self.cfgs["csv"] = os.getcwd()
            self.cfgs["lua"] = os.getcwd()
            self.cfgs["lastpath"] = os.getcwd()
            self.save()
        else:
            with open("config.cfg", "r") as f:
                self.cfgs = json.load(f)

    def save(self):
        with open("config.cfg", "w") as of:
            json.dump(self.cfgs, of)

    def getLastFilePath(self):
        return self.cfgs.get("lastpath", os.getcwd())

    def onLastFileSelect(self, filePath):
        self.cfgs["lastpath"] = filePath
        self.save()

    def getCsvPath(self):
        return self.cfgs["csv"]
    
    def getLuaPath(self):
        return self.cfgs["lua"]

    def onModifyCsvPath(self, path):
        self.cfgs["csv"] = path
        self.save()

    def onModifyLuaPath(self, path):
        self.cfgs["lua"] = path
        self.save()

instCfg = ConfigParam()


class ConvertorThread(QThread):
    signalEvent = pyqtSignal(str)

    def __init__(self, files, parent = None):
        super(ConvertorThread, self).__init__(parent)
        self.files = files

    def run(self):
        for fd in self.files:
            self.signalEvent.emit(fd)
            try:
                wb = xlrd.open_workbook(fd)
                sheets = wb.sheet_names()[:]
                for i in sheets:
                    self.signalEvent.emit("\t" + i + ".csv")
                    data = pandas.read_excel(fd, header = None, encoding = u'utf-8', sheet_name = i)
                    data.to_csv(os.path.join(instCfg.getCsvPath(), i.strip() + ".csv"), encoding = u'gb18030', index=False, header = None)
                    time.sleep(0.1)
            except Exception as e:
                self.signalEvent.emit(str(e))
        self.signalEvent.emit("Finish!!![%s]" % time.strftime("%H:%M:%S"))

LUA_HEADER = """
----------------------------------------------------------------
--此文件是由xlsx_csv/lua工具自动导出，请勿手动修改
----------------------------------------------------------------

"""

class ConvertorLuaThread(QThread):
    signalEvent = pyqtSignal(str)

    def __init__(self, files, parent = None):
        super(ConvertorLuaThread, self).__init__(parent)
        self.files = files

    def gao(self, sheetName, sheet):
        if sheet.nrows < 3:
            self.signalEvent.emit("[%s]不足三行，无视" % sheetName)
            return
        print(sheet.nrows, sheet.ncols)
        isKey = sheet.cell(2, 0).value == "key"
        with open(os.path.join(instCfg.getLuaPath(), sheetName.strip() + ".lua"), "w") as of:
            print(LUA_HEADER, file = of)
            print("local %s = {" % sheetName, file = of)
            for i in range(3,5):
                if isKey:
                    print("[%s]={" % int(sheet.cell(i, 0).value), file = of)
                else:
                    print("[%s]={" % sheet.cell(i, 0).value, file = of)
                for j in range(1, sheet.ncols):
                    k = sheet.cell(2, j).value
                    tp = sheet.cell(1, j).value
                    if len(k) < 1 or len(tp) < 1: continue


    def run(self):
        for fd in self.files:
            self.signalEvent.emit(fd)
            try:
                wb = xlrd.open_workbook(fd)
                sheets = wb.sheet_names()[:]
                for i in sheets:
                    self.signalEvent.emit("\t" + i + ".lua")
                    self.gao(i, wb.sheet_by_name(i))
                    time.sleep(0.1)
            except Exception as e:
                traceback.print_exc(5)
                self.signalEvent.emit("ERROR: " + str(e))
        self.signalEvent.emit("Finish!!![%s]" % time.strftime("%H:%M:%S"))

class ConvertorWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.workingThread = None
        self.luaThread = None

        self.initUI()
        self.setFixedSize(self.width(), self.height())
        self.show()

    def updateTextBrowserCursor(self):
        cursor = self.textBrowser.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.textBrowser.setTextCursor(cursor)

    def addTextBrowser(self):
        self.textBrowser = QTextBrowser(self)
        self.textBrowser.resize(WINDOW_WIDTH - 60, WINDOW_HEIGHT - 200)
        self.textBrowser.move(30, 20)
        font = QFont("Courier New")
        font.setPointSize(8)
        self.textBrowser.setFont(font)
        self.updateTextBrowserCursor()
        self.textBrowser.append("csv path:[%s]" % instCfg.getCsvPath())
        self.textBrowser.append("lua path:[%s]" % instCfg.getLuaPath())

    def addFileSelect(self):
        self.openFileButton = QPushButton("选择转换文件csv", self)
        self.openFileButton.clicked.connect(self.setOpenFile)
        self.openFileButton.move(50, 350)
    
    def onMessage(self, msg):
        self.textBrowser.append(msg)

    def setOpenFile(self):
        files, what = QFileDialog.getOpenFileNames(self, "选择要转换的文件(可多选)", directory = instCfg.getLastFilePath(), filter = "Xlsx Files(*.xlsx)")
        if files:
            instCfg.onLastFileSelect(files[0])
            if self.workingThread: self.workingThread = None
            self.workingThread = ConvertorThread(files)
            self.workingThread.signalEvent.connect(self.onMessage)
            self.workingThread.start()

    def onModifyCsvPath(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self, "选择文件夹", instCfg.getCsvPath(), options)
        if directory:
            instCfg.onModifyCsvPath(directory)
            self.textBrowser.append("修改csv路径成功[%s]" % instCfg.getCsvPath())

    def addCsvPathModifyButton(self):
        self.csvPathModifyButton = QPushButton("修改csv路径", self)
        self.csvPathModifyButton.move(200, 350)
        self.csvPathModifyButton.clicked.connect(self.onModifyCsvPath)

    def onOpenCsvDir(self):
        os.startfile(instCfg.getCsvPath())
        self.textBrowser.append("打开csv目录成功")

    def addOpenDirButton(self):
        self.csvDirOpenBtn = QPushButton("打开csv目录", self)
        self.csvDirOpenBtn.move(350, 350)
        self.csvDirOpenBtn.clicked.connect(self.onOpenCsvDir)

    def addTestButton(self):
        self.tstButton = QPushButton("ok", self)
        self.tstButton.move(30,30)
        self.tstButton.clicked.connect(lambda : self.textBrowser.append(time.strftime("%H:%M:%S")))

    def setOpenFileForLua(self):
        files, what = QFileDialog.getOpenFileNames(self, "选择要转换的文件(可多选)", directory = instCfg.getLastFilePath(), filter = "Xlsx Files(*.xlsx)")
        if files:
            instCfg.onLastFileSelect(files[0])
            if self.luaThread: self.luaThread = None
            self.luaThread = ConvertorLuaThread(files)
            self.luaThread.signalEvent.connect(self.onMessage)
            self.luaThread.start()

    def addFileSelectForLua(self):
        self.openFileButtonLua = QPushButton("选择转换文件lua", self)
        self.openFileButtonLua.clicked.connect(self.setOpenFileForLua)
        self.openFileButtonLua.move(50, 400)

    def onModifyLuaPath(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self, "选择文件夹", instCfg.getLuaPath(), options)
        if directory:
            instCfg.onModifyLuaPath(directory)
            self.textBrowser.append("修改lua路径成功[%s]" % instCfg.getLuaPath())

    def addLuaPathModifyButton(self):
        self.luaPathModifyButton = QPushButton("修改lua路径", self)
        self.luaPathModifyButton.move(200, 400)
        self.luaPathModifyButton.clicked.connect(self.onModifyLuaPath)

    def onOpenLuaDir(self):
        os.startfile(instCfg.getLuaPath())
        self.textBrowser.append("打开lua目录成功")

    def addOpenLuaDirButton(self):
        self.luaDirOpenBtn = QPushButton("打开lua目录", self)
        self.luaDirOpenBtn.move(350, 400)
        self.luaDirOpenBtn.clicked.connect(self.onOpenLuaDir)

    def initUI(self):

        self.addTextBrowser()
        # self.addTestButton()
        self.addFileSelect()
        self.addCsvPathModifyButton()
        self.addOpenDirButton()

        self.addFileSelectForLua()
        self.addLuaPathModifyButton()
        self.addOpenLuaDirButton()

        # self.setGeometry(300, 300, 600, 520)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        # self.setWindowTitle('Test Icon')
        self.setWindowIcon(QIcon('icon.ico'))


def gao():
    app = QApplication(sys.argv)
    app.setApplicationName("xlsx_csv/lua转换器")
    instCfg.load()
    window = ConvertorWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    gao()
