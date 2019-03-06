#coding=utf-8
'''
Created on 2017/8/8 18:46:03

@author: tys
'''


import sys
import pika
import time
import json


class ExecException(Exception):
    "ServerCtrl error"

class PiKaClass(object):

    def __init__(self, user, pswd, ip, port):
        self.credentials = pika.PlainCredentials(user, pswd)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(ip,port,"/", self.credentials))
        self.channel = self.connection.channel()

    def publish(self, svrid, msg):
        self.channel.basic_publish(exchange='amq.direct',
                  routing_key='%d_php' % svrid,
                  body = msg)

class ServerCtrl(object):

    def __init__(self):
        self.inicfg = {}
        self.pikaq = None

    def loadini(self):
        f = open("GameServer.ini", "r")
        section = ""
        for line in f:
            if len(line) < 2 or line.startswith("#"):
                continue
            if line.startswith("["):
                section = line[1:-2]
            else:
                pos = line.find("=")
                if pos == -1:
                    raise ExecException("GameServer.ini error[%s]" % line[:-1])
                    continue
                l = line[:pos]
                r = line[pos + 1:-1]
                kv = self.inicfg.get(section, {})
                kv[l]=r
                self.inicfg[section]=kv
        f.close()

    def get(self, section, key):
        kv = self.inicfg.get(section, {})
        v = kv.get(key)
        if not v:
            raise ExecException("GameServer.ini not contains [%s]:[%s]" % (section, key))
        return v

    def svrid():
        return int(self.get("server", "server_id"))

    def buildPika(self):
        brokerUser = self.get("broker", "account")
        brokerPswd = self.get("broker", "password")
        brokerIP = self.get("broker", "ip")
        brokerPort = int(self.get("broker", "port"))
        self.pikaq = PiKaClass(brokerUser, brokerPswd, brokerIP, brokerPort)

    def buildBasicMsg(self, status):
        orderid =  time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        admin = "ServerCtrl"
        svrid = int(self.get("server", "server_id"))
        msg = {"orderid":orderid,"admin":admin,"servers":svrid,"msgid":1030,"status":status}
        return json.dumps(msg)

    def pause(self):
        self.buildPika()
        msg= self.buildBasicMsg(1)
        self.pikaq.publish(self.svrid(), msg)

    def resume(self):
        self.buildPika()
        msg= self.buildBasicMsg(2)
        self.pikaq.publish(self.svrid(), msg)
    

instance = ServerCtrl()

helpstr = """
            -pause  pause server
            -resume resume server
"""

enable_args = ["-pause", "-resume"]

def gao():
    try:
        args = sys.argv
        if len(args) != 2:
            print helpstr
            return
        if args[1] not in enable_args:
            print helpstr
            return
        instance.loadini()
        if enable_args[0] == args[1]:
            instance.pause()
        else:
            instance.resume()
    except Exception, e:
        print unicode(e)

if __name__ == '__main__':
    gao()
    print("Done!")

