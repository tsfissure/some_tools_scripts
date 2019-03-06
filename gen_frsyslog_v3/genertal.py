#coding=utf-8
'''
Created on 2018/9/11 11:32:42

@author: tys
'''

import json

toper = """
module(load="ommysql.so")

template(name="locallog" type="string" string="/var/log/frlog/%$year%-%$month%-%$day%.log")

# for 360
template(name="log360" type="string" string="/data/gameinfo/%msg:F,96:2%/act.log")
template(name="log360FileTmpl" type="string" string="%msg:F,96:3%\\r\\n")
"""

header = """
ruleset(name="frlog" queue.workerThreads="10"){
    action(type="omfile" dynaFile="locallog")
    if $msg startswith ' log360' and re_match($msg, "(.*`){2,}") then {
        action(type="omfile" dynaFile="log360" template="log360FileTmpl")
    }
    if prifilt("local1.*") then {"""

footer = """        }
        stop
        #PS：请给这个登录账号在这个数据库上所有权限
    }
}"""


class DataServers:

    def __init__(self):
        self.svrs = {}

    def load(self):
        self.svrs = json.load(open("servers.json"))

    def get(self, mid):
        return self.svrs.get(str(mid), None)

    def getsvrs(self):
        return self.svrs

servers = DataServers()

class CfgGenerator:

    def __init__(self):
        self.action = self.getTabstop(3) + 'action(type="ommysql" server="%s" serverport="%s" db="%s" uid="%s" pwd="%s" template="%s")'

    def fillAction(self, js, tpl):
        return self.action % (js["host"], js["port"], js["db"], js["user"], js["pswd"], tpl)

    def getTabstop(self, cnt):
        return "".join([" "] * cnt * 4)

    def writeToper(self, f):
        print >> f, toper

    def writeHeader(self, f):
        print >> f, header

    def writeFooter(self, f):
        print >> f, footer

    def writeTemplate(self, f):
        msg = '%s\ntemplate (name="%s" type="string" option.sql="on"\n    string="call %s(%s)")\n'
        param = '\'%%msg:F,96:%d%%\''
        with open("message.cfg", "r") as mf:
            for line in mf:
                lst = line[:-1].split(',')
                if len(lst) < 4: continue
                tmp = ""
                param_cnt = int(lst[3])
                for i in xrange(2, 2 + param_cnt):
                    tmp += param % i + ","
                tmp = tmp[:-1]
                print >> f, msg % (lst[0],lst[1],lst[2],tmp)

    def writeAction(self, f):
        # act = "action(type=\"ommysql\" server=\"%s\" serverport=\"%d\" db=\"%s\" uid=\"%s\" pwd=\"%s\" template=\"%s\")"
        oriifmsg = "if $msg startswith ' %s' and re_match($msg, \"(.*`){%s,}\") then {"
        mulifmsg = "if $msg startswith ' %s' then {"
        firstIfMsg = True
        svrs = servers.getsvrs()
        for sid, svr in svrs.iteritems():
            if not svr: break
            ifmsg = oriifmsg
            print >> f, self.getTabstop(2) + mulifmsg % sid
            firstAction = True
            with open("message.cfg", "r") as mf:
                for line in mf:
                    lst = line[:-1].split(',')
                    if len(lst) < 4: continue
                    tmp = ""
                    print >> f, self.getTabstop(3)+ (ifmsg % (str(sid) + lst[2], lst[3]))
                    print >> f, self.getTabstop(1) + self.fillAction(svr, lst[1])
                    if firstAction:
                        ifmsg = "} else " + ifmsg
                        firstAction = False
                print >> f, self.getTabstop(3) + "}"
            if firstIfMsg:
                mulifmsg = "} else " + mulifmsg
                firstIfMsg = False

    def execute(self):
        with open("frlog_auto.conf", "w") as f:
            self.writeToper(f)
            self.writeTemplate(f)
            self.writeHeader(f)
            self.writeAction(f)
            self.writeFooter(f)

instance = CfgGenerator()


if __name__ == '__main__':
    servers.load()
    instance.execute()


