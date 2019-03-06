#coding=utf-8
'''
Created on 2018/9/6 11:09:53

@author: tys
'''

from sshtunnel import SSHTunnelForwarder
import MySQLdb


gFakeClinetSet = {}


class FakerClient(object):

    def __init__(self):
        self.ssh = None
        self.mysql = None
        self.dbname = None
        self.sql = ""

    def loadSql(self, fileName):
        self.sql = ""
        with open(fileName, "r") as f:
            for line in f:
                self.sql += line[:-1] + " "

    def connectSSH(self):
        print "ssh connecting..."
        self.ssh = SSHTunnelForwarder(
                ("ip", 5650),
                ssh_password = "password",
                ssh_username = "root",
                remote_bind_address = ("127.0.0.1", 3306)
                )
        pass

    def connectMySQL(self, dbname):
        if self.dbname == dbname:
            return
        if self.mysql:
            self.mysql.close()
        print u'ssh start...'
        self.ssh.start()
        print u'mysql connecting...'
        self.mysql = MySQLdb.connect(host = "127.0.0.1",
                port = self.ssh.local_bind_port,
                user = "root",
                passwd = "123456",
                db = dbname,
                charset = 'utf8')
        self.dbname = dbname
        print u'mysql connected'
        pass

    def close(self):
        print u'close...'
        if self.mysql:
            self.mysql.close()
            self.mysql = None
        if self.ssh:
            self.ssh.close()
            self.ssh = None

    def execute(self, sql, params):
        print u'start query...'
        c = self.mysql.cursor()
        c.execute(sql, params)
        rows = c.fetchall()
        c.close()
        print u'query end...'
        return rows
    
    def gao(self):
        assert False, "gao() is not implemented"

    def prepare(self):
        assert False, "prepare() is not implemented"

    def register(self, id):
        global gFakeClinetSet
        if gFakeClinetSet.get(id, None):
            raise ValueError('dumplicate id[%d]' % id)
        gFakeClinetSet[id] = self

