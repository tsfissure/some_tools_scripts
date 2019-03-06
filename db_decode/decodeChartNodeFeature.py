#coding=utf-8
'''
Created on 2018/12/11 15:10:35

@author: tys
'''

import traceback
import yhjxbase64

def printer(bins):
    # bins = basic.instance
    fmter = "%10s = %s"
    print fmter % ("version", bins.nextInt())
    print fmter % ("id", bins.nextLong())
    print fmter % ("sex", bins.nextInt())
    print fmter % ("horse", bins.nextInt())
    print fmter % ("weapon", bins.nextInt())
    print fmter % ("wing", bins.nextInt())
    print fmter % ("funclv", bins.nextInt())
    print fmter % ("qqdiamond", bins.nextInt())
    print fmter % ("flyLevel", bins.nextInt())
    print fmter % ("helpbattle", bins.nextInt())
    print fmter % ("fashion", bins.nextInt())
    if bins.hasValue():
        print fmter % ("fightValue", bins.nextLong())
    if bins.hasValue():
        print fmter % ("param", bins.nextLong())

if __name__ == '__main__':
    try:
        yhjxbase64.instance.load()
        yhjxbase64.instance.display(printer)
    except Exception, e:
        print unicode(e)
        traceback.print_exc(5)
    raw_input('Done!')

