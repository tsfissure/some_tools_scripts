#coding=utf-8
'''
Created on 2019/5/28 17:01:22

@author: tys
'''

import sys, os, json, time
import pandas, xlrd
from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QTextBrowser, QPushButton,
        QGridLayout, QFileDialog)
from PyQt5.QtGui import QIcon, QFont


class ConfigParam(object):

    def __init__(self):
        self.cfgs = {}

    def load(self):
        if not os.path.exists("config.cfg"):
            self.cfgs["csv"] = os.getcwd()
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

    def onModifyCsvPath(self, path):
        self.cfgs["csv"] = path
        self.save()

instCfg = ConfigParam()

class ConvertorWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.show()


    def tryConvert(self, files):
        for fd in files:
            self.textBrowser.append(fd)
            try:
                wb = xlrd.open_workbook(fd)
                sheets = wb.sheet_names()[:]
                for i in sheets:
                    self.textBrowser.append(i)
                    data = pandas.read_excel(fd, header = None, encoding = u'utf-8', sheet_name = i)
                    data.to_csv(os.path.join(instCfg.getCsvPath(), i.strip() + ".csv"), encoding = u'gbk', index=False, header = None)
            except Exception as e:
                self.textBrowser.append(e)
        self.textBrowser.append("Finish!!![%s]" % time.strftime("%H:%M:%S"))

    def addTextBrowser(self):
        self.textBrowser = QTextBrowser(self)
        self.textBrowser.resize(540, 300)
        self.textBrowser.move(30, 20)
        # self.textBrowser.setFontPointSize(14)
        font = QFont("Courier New")
        font.setPointSize(11)
        self.textBrowser.setFont(font)
        self.textBrowser.append("csv path:[%s]" % instCfg.getCsvPath())

    def addFileSelect(self):
        self.openFileButton = QPushButton("选择转换文件", self)
        self.openFileButton.clicked.connect(self.setOpenFile)
        self.openFileButton.move(50, 350)

    def setOpenFile(self):
        files, what = QFileDialog.getOpenFileNames(self, "选择要转换的文件(可多选)", directory = instCfg.getLastFilePath(), filter = "Xlsx Files(*.xlsx)")
        if files:
            instCfg.onLastFileSelect(files[0])
            self.tryConvert(files)

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

    def addTestButton(self):
        self.tstButton = QPushButton("ok", self)
        self.tstButton.move(30,30)
        self.tstButton.clicked.connect(lambda : self.textBrowser.append(time.strftime("%H:%M:%S")))

    def initUI(self):

        self.addTextBrowser()
        # self.addTestButton()
        self.addFileSelect()
        self.addCsvPathModifyButton()

        # self.setGeometry(300, 300, 600, 520)
        self.resize(600, 420)
        self.setWindowTitle('Test Icon')
        self.setWindowIcon(QIcon('icon.ico'))


def gao():
    app = QApplication(sys.argv)
    app.setApplicationName("Xlsx2Csv Convertor")
    instCfg.load()
    window = ConvertorWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    gao()
