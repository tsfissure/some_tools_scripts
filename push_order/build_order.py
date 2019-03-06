#coding=utf-8
'''
Created on 2018/12/24 20:13:55

@author: tys
'''

import json
import time
import traceback


def gaoJson(js):
    timeArray = time.strptime(js["time"], "%Y-%m-%d %H:%M:%S")
    js["time"] = int(time.mktime(timeArray))
    info = {
            "interface":"recharge",
            "gname":"yhjx",
            "gid":191,
            "dept":38,
            "channel":"",
            "legoin":0
            }
    msg = ""
    for k, v in info.iteritems():
        msg += "&" + str(k) + "=" + str(v)
    for k, v in js.iteritems():
        msg += "&" + str(k) + "=" + str(v)
    msg = "gameinfo " + msg[1:]
    sid = js.get("sid")
    sidInt = int(sid[1:])
    print sidInt
    with open("./%s/act.log" % sidInt, "a") as f:
        print >> f, msg

def gao():
    cfg = json.load(open('data.cfg'))
    for c in cfg:
        gaoJson(c)


if __name__ == '__main__':
    try:
        gao()
    except Exception, e:
        print e
        traceback.print_exc(5)
    raw_input('Done!')


