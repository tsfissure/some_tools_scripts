#coding=utf-8
'''
Created on 2018/11/8 15:56:43

@author: tys
'''

import codecs

header = """<?php

return [

    'getway' => ["""

footer = """
    ],

    'other' => [
        'theme' => 'default',

        'paths' => [
            resource_path('views/vendor/mail'),
        ],
    ]
];
"""


class GameChannel(object):

    def __init__(self):
        self.cppLst = []
        self.luaLst = []

    def loadConfig(self):
        cppPath = ""
        luaPath = ""
        with open("path.cfg", "r") as f:
            for line in f:
                if line.startswith("cpp="):
                    cppPath = line[4:-1]
                elif line.startswith("lua="):
                    luaPath = line[4:-1]
        with codecs.open(cppPath, encoding = 'GB2312') as f:
            cppstart = False
            for line in f:
                if '^pass' in line: continue
                if "enum CommonChannel" in line:
                    cppstart = True
                    continue
                if not cppstart: continue
                if "};" in line:
                    break
                msg = line[:-1]
                self.cppLst.append(msg.encode("UTF-8"))
        with codecs.open(luaPath, encoding = 'UTF-8') as f:
            for line in f:
                msg = line[:-1]
                self.luaLst.append(msg.encode("UTF-8"))

    def execute(self):
        with open("game.php", "w") as f:

            def inputer(msg):
                print >> f, '\t\t', msg

            def inputLua(line):
                if '^pass' in line: return
                lst = line[:-1].split('=')
                if len(lst) > 1:
                    lst1 = lst[1].split('--') 
                    if len(lst1) > 1:
                        lst2 = lst1[1].split('&')
                        if len(lst2) > 1:
                            lst2[1] = lst2[1].strip()
                            lst3 = lst2[1].split('][')
                            if len(lst3) > 1:
                                key = [int(i) for i in lst3[0][1:].split(',')]
                                val = lst3[1][:-1].split(',')
                                if len(key) == len(val):
                                    basic = int(lst1[0].strip())
                                    for i in xrange(len(key)):
                                        k = int(key[i])
                                        v = val[i]
                                        msg = "'%s'=>'%s'," % (basic*1000+k, v)
                                        inputer(msg)
                            else:
                                msg = "'%s'=>'%s'," % (lst1[0].strip(), lst1[1].strip())
                                inputer(msg)
                        else:
                            msg = "'%s'=>'%s'," % (lst1[0].strip(), lst1[1].strip())
                            inputer(msg)

            def inputCpp(line):
                if '^pass' in line: return
                lst = line[:-1].split('=')
                if len(lst) > 1:
                    lst1 = lst[1].split('//') 
                    if len(lst1) > 1:
                        lst2 = lst1[1].split('&')
                        if len(lst2) > 1:
                            lst2[1] = lst2[1].strip()
                            lst3 = lst2[1].split('][')
                            if len(lst3) > 1:
                                key = [int(i) for i in lst3[0][1:].split(',')]
                                val = lst3[1][:-1].split(',')
                                if len(key) == len(val):
                                    basic = int(lst1[0].strip())
                                    for i in xrange(len(key)):
                                        k = int(key[i])
                                        v = val[i]
                                        msg = "'%s'=>'%s'," % (basic*1000+k, v)
                                        inputer(msg)
                            else:
                                msg = "'%s'=>'%s'," % (lst1[0].strip()[:-1], lst1[1].strip())
                                inputer(msg)
                        else:
                            msg = "'%s'=>'%s'," % (lst1[0].strip()[:-1], lst1[1].strip())
                            inputer(msg)

            print >> f, header
            for cpp in self.cppLst:
                inputCpp(cpp)
            for lua in self.luaLst:
                inputLua(lua)
            print >> f, footer


instance = GameChannel()

if __name__ == '__main__':
    instance.loadConfig()
    instance.execute()
    raw_input('Done!')

