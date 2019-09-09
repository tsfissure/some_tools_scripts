#coding=utf-8
'''
Created on 2019/7/23 16:01:13

@author: tsfissure
'''

import sys

XML_HEADER = """<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE sqlMap PUBLIC "-//ibatis.apache.org//DTD SQL Map 2.0//EN" "http://ibatis.apache.org/dtd/sql-map-2.dtd">
<sqlMap> """

XML_FOOTER = """
</sqlMap>"""

PACKAGE_NAME = "com.xianxia.bus"
if int(sys.argv[-1]) == 1:
    PACKAGE_NAME = "com.xianxia.webbus"

JAVA_ENTITY_HEADER = """package %s.%s.entity;

import com.kernel.db.dao.AbsVersion;
import com.kernel.db.dao.IEntity;
import com.kernel.pojo.annotation.Column;
import com.kernel.pojo.annotation.Primary;
import com.kernel.pojo.annotation.Table;

import java.io.Serializable;

"""

JAVA_DAO_HEADER = """package %s.%s.dao;

import com.kernel.bus.share.dao.XXBusAbsCacheDao;
import com.kernel.db.accessor.AccessType;
import com.kernel.db.dao.IDaoOperation;
import org.springframework.stereotype.Repository;;

"""

JAVA_EASY_ACTION_HEADER = """package %s.%s.easyaction;

import com.kernel.easymapping.annotation.EasyMapping;
import com.kernel.easymapping.annotation.EasyWorker;
import com.kernel.pool.executor.Message;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

"""

JAVA_EXPORT_SVCE_HEADER = """package %s.%s.export;

"""

JAVA_SERVICE_HEADER = """package %s.%s.service;
"""

if __name__ == '__main__':
    pass

