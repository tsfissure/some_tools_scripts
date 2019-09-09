#coding=utf-8
'''
Created on 2019/7/23 16:04:59

@author: tsfissure
'''
def convertJavaName(name):
    rlt = ""
    first = False
    for i in name:
        if '_' == i:
            first = True
            continue
        if first:
            rlt += i.upper()
            first = False
        else:
            rlt += i
    return rlt

def convertEntity(name):
    rlt = ""
    first = True
    for i in name:
        if '_' == i:
            first = True
            continue
        if first:
            rlt += i.upper()
            first = False
        else:
            rlt += i
    return rlt + "Entity"

def convertClassName(name):
    rlt = ""
    first = True
    for i in name:
        if '_' == i:
            first = True
            continue
        if first:
            rlt += i.upper()
            first = False
        else:
            rlt += i
    return rlt

if __name__ == '__main__':
    pass

