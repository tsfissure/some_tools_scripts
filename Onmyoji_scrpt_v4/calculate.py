#coding=utf-8
'''
Created on 2019/7/17 12:49:54

@author: tsfissure
'''

import aircv

imgSrc = aircv.imread("a.png")
imgSch = aircv.imread("img\challenge.png")

rlt = aircv.find_template(imgSrc, imgSch)

print(rlt)


if __name__ == '__main__':
    pass

