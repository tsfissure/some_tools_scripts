#coding=utf-8
'''
Created on 2019/7/23 15:57:05

@author: tsfissure
'''

import pymysql
import traceback
import json
import os
import utils
import const


class DataBase2JavaFilesConvertor(object):

    def __init__(self):
        self.mOutPutFileStream = None
        self.mTableName = ""
        self.mColumnNameList = []
        self.mPrimaryKey = None

        self.mResultMapName = ""
        self.mEntityTableName = ""
        self.mClassTableName = ""

    def setType(self, tp):
        self.genType = tp # 0 or 1, 1 is web server

    def LoadConfig(self):
        with open("config.cfg", "r") as f:
            self.cfg = json.load(f)
            entity = self.cfg["entity"]
            if entity.endswith("Entity"):
                entity = entity[:len(entity) - len("Entity")]
            self.cfg["noentity"] = entity # 去掉entity结尾
            self.cfg["dirname"] = entity.lower()
            if self.genType == 1:
                self.cfg["package"] = "com.xianxia.webbus.%s.entity" % self.cfg["dirname"]
            else:
                self.cfg["package"] = "com.xianxia.bus.%s.entity" % self.cfg["dirname"]

    def WriteMsg(self, msg):
        print(msg, file = self.mOutPutFileStream)

    def ResultMap(self):
        self.WriteMsg('\t<resultMap id="%s" class="%s.%s" > ' % (self.mResultMapName, self.cfg["package"], self.mEntityTableName))
        for i in self.mColumnNameList:
            self.WriteMsg('\t\t<result property="%s" column="%s"/>' % (utils.convertJavaName(i), i))
        self.WriteMsg("\t</resultMap>\n")

    def QueryCondition(self):
        self.WriteMsg('\t<sql id="queryCondition%s">' % self.mEntityTableName)
        self.WriteMsg('\t\t<dynamic prepend="where">')
        for i in self.mColumnNameList:
            self.WriteMsg('\t\t\t<isNotNull prepend="and" property="%s"> %s = #%s# </isNotNull>' % (utils.convertJavaName(i), i, utils.convertJavaName(i)))
        self.WriteMsg('\t\t</dynamic>')
        self.WriteMsg('\t</sql>\n')

    def QueryByKey(self):
        if self.mPrimaryKey:
            self.WriteMsg('\t<sql id="queryByKey%s">' % self.mClassTableName)
            self.WriteMsg('\t\twhere %s = #%s#' % (self.mPrimaryKey, utils.convertJavaName(self.mPrimaryKey)))
            self.WriteMsg('\t</sql>\n')

    def InsertEntity(self):
        self.WriteMsg('\t<insert id="insert%s" parameterClass="%s.%s">' % (self.mEntityTableName, self.cfg["package"], self.mEntityTableName))
        self.WriteMsg('\t\tinsert into %s(' % self.mTableName)
        first = True
        for i in self.mColumnNameList:
            self.WriteMsg('\t\t<isNotNull prepend="%s" property="%s"> %s </isNotNull>' % ("" if first else ",", utils.convertJavaName(i), i))
            first = False
        self.WriteMsg('\t\t)\n\t\tvalues(')
        first = True
        for i in self.mColumnNameList:
            ni = utils.convertJavaName(i)
            self.WriteMsg('\t\t<isNotNull prepend="%s" property="%s"> #%s# </isNotNull>' % ("" if first else ",", ni, ni))
            first = False
        self.WriteMsg('\t\t)')
        self.WriteMsg('\t</insert>\n')

    def DeleteEntity(self):
        self.WriteMsg('\t<delete id="delete%s">' % self.mEntityTableName)
        self.WriteMsg('\t\tdelete from %s' % self.mTableName)
        self.WriteMsg('\t\t<include refid="queryByKey%s"/>' % self.mClassTableName)
        self.WriteMsg('\t</delete>\n')

    def Update(self):
        self.WriteMsg('\t<update id="update%s" parameterClass="%s.%s">' % (self.mEntityTableName, self.cfg["package"], self.mEntityTableName))
        self.WriteMsg('\t\tupdate %s' % self.mTableName)
        self.WriteMsg('\t\t<dynamic prepend="set">')
        for i in self.mColumnNameList:
            self.WriteMsg('\t\t\t<isNotNull prepend="," property="%s"> %s = #%s# </isNotNull>' % (utils.convertJavaName(i), i, utils.convertJavaName(i)))
        self.WriteMsg('\t\t</dynamic>')
        self.WriteMsg('\t\t<include refid="queryByKey%s"/>' % self.mClassTableName)
        self.WriteMsg('\t</update>\n')

    def SelectSingle(self):
        self.WriteMsg('\t<select id="selectSingle%s" resultMap="%s">' % (self.mEntityTableName, self.mResultMapName))
        self.WriteMsg('\t\tselect')
        self.WriteMsg('\t\t%s' % "\n\t\t,".join(self.mColumnNameList))
        self.WriteMsg('\t\tfrom %s' % self.mTableName)
        self.WriteMsg('\t\t<include refid="queryByKey%s"/>' % self.mClassTableName)
        self.WriteMsg('\t</select>\n')

    def SelectCnt(self):
        self.WriteMsg('\t<select id="selectRecordsCount%s" parameterClass="java.util.Map" resultClass="java.lang.Integer">' % self.mEntityTableName)
        self.WriteMsg('\t\tselect count(*) from %s' % self.mTableName)
        self.WriteMsg('\t\t<include refid="queryCondition%s"/>' % self.mEntityTableName)
        self.WriteMsg('\t</select>\n')

    def SelectPage(self):
        self.WriteMsg('\t<select id="selectMultiPaging%s" parameterClass="java.util.Map" resultMap="%s">' % (self.mEntityTableName, self.mResultMapName))
        self.WriteMsg('\t\tselect')
        self.WriteMsg('\t\t%s' % "\n\t\t,".join(self.mColumnNameList))
        self.WriteMsg('\t\tfrom %s' % self.mTableName)
        self.WriteMsg('\t\t<include refid="queryCondition%s"/>' % self.mEntityTableName)
        self.WriteMsg('\t\tlimit #start#,#pagesize#')
        self.WriteMsg('\t</select>\n')

    def SelectMulti(self):
        self.WriteMsg('\t<select id="selectMulti%s" parameterClass="java.util.Map" resultMap="%s">' % (self.mEntityTableName, self.mResultMapName))
        self.WriteMsg('\t\tselect')
        self.WriteMsg('\t\t%s' % "\n\t\t,".join(self.mColumnNameList))
        self.WriteMsg('\t\tfrom %s' % self.mTableName)
        self.WriteMsg('\t\t<include refid="queryCondition%s"/>' % self.mEntityTableName)
        self.WriteMsg('\t</select>\n')

    def SelectAll(self):
        self.WriteMsg('\t<select id="selectAll%s" resultMap="%s">' % (self.mEntityTableName, self.mResultMapName))
        self.WriteMsg('\t\tselect')
        self.WriteMsg('\t\t%s' % "\n\t\t,".join(self.mColumnNameList))
        self.WriteMsg('\t\tfrom %s' % self.mTableName)
        self.WriteMsg('\t</select>\n')

    def SelectSingleParam(self):
        self.WriteMsg('\t<select id="selectSingleByParams%s" resultMap="%s">' % (self.mEntityTableName, self.mResultMapName))
        self.WriteMsg('\t\tselect')
        self.WriteMsg('\t\t%s' % "\n\t\t,".join(self.mColumnNameList))
        self.WriteMsg('\t\tfrom %s' % self.mTableName)
        self.WriteMsg('\t\t<include refid="queryCondition%s"/>' % self.mEntityTableName)
        self.WriteMsg('\t</select>')

    def CheckDirectory(self, name):
        dirs = os.path.join("out", self.cfg["dirname"], name)
        if self.genType == 1:
            dirs = os.path.join("out_web", self.cfg["dirname"], name)
        if not os.path.exists(dirs):
            os.makedirs(dirs)
        return dirs
    
    def TryXMLFile(self):
        dirs = self.CheckDirectory("sqlmap")
        fd = os.path.join(dirs, self.mEntityTableName + ".xml")
        with open(fd, "w") as of:
            self.mOutPutFileStream = of
            self.WriteMsg(const.XML_HEADER)
            self.ResultMap()
            self.QueryCondition()
            self.QueryByKey()
            self.InsertEntity()
            self.DeleteEntity()
            self.Update()
            self.SelectSingle()
            self.SelectCnt()
            self.SelectPage()
            self.SelectMulti()
            self.SelectAll()
            self.SelectSingleParam()
            self.WriteMsg(const.XML_FOOTER)

    def TryGenerateXMLFile(self):
        self.mPrimaryKey = None
        self.mColumnNameList = []
        for i in self.mDatas:
            self.mColumnNameList.append(i[1])
            if i[2] == "PRI":
                self.mPrimaryKey = i[1]
        self.TryXMLFile()

    def TryDAO(self):
        dirs = self.CheckDirectory("dao")
        fd = os.path.join(dirs, self.cfg["noentity"] + "Dao.java")
        with open(fd, "w") as of:
            self.mOutPutFileStream = of
            self.WriteMsg(const.JAVA_DAO_HEADER % (const.PACKAGE_NAME, self.cfg["dirname"]))
            self.WriteMsg("@Repository")
            noentity = self.cfg["noentity"]
            self.WriteMsg("public class %sDao extends XXBusAbsCacheDao<%s> implements IDaoOperation<%s> {" % (noentity, self.mEntityTableName, self.mEntityTableName))
            self.WriteMsg("\n\n}\n")

    def TryEasyAction(self):
        dirs = self.CheckDirectory("easyaction")
        fd = os.path.join(dirs, self.cfg["noentity"] + "Action.java")
        with open(fd, "w") as of:
            self.mOutPutFileStream = of
            self.WriteMsg(const.JAVA_EASY_ACTION_HEADER % (const.PACKAGE_NAME, self.cfg["dirname"]))
            if self.genType == 1:
                self.WriteMsg("@Controller\n@WebEasyWorker(tableName = \"%s\", groupName = EasyGroup.WEB_BUS)" % self.cfg["table"])
                self.WriteMsg("public class %sAction extends AbsWebAction<%sService> {" % (self.cfg["noentity"], self.cfg["noentity"]))
            else:
                self.WriteMsg("@Component\n@EasyWorker(moduleName = )")
                self.WriteMsg("public class %sAction {" % self.cfg["noentity"])
            self.WriteMsg("\n\n}\n")

    def GetVarType(self, tp):
        tps = self.cfg.get("type", None)
        if not tps: return "Integer"
        rlt = tps.get(tp, "Integer")
        return rlt

    def TryEntity(self):
        dirs = self.CheckDirectory("entity")
        fd = os.path.join(dirs, self.cfg["entity"] + ".java")
        with open(fd, "w", encoding="utf8") as of:
            self.mOutPutFileStream = of
            self.WriteMsg(const.JAVA_ENTITY_HEADER % (const.PACKAGE_NAME, self.cfg["dirname"]))
            self.WriteMsg('@Table(name = "%s")' % self.cfg["table"])
            self.WriteMsg('public class %s  extends AbsVersion implements Serializable, IEntity {\n' % self.mEntityTableName)
            pkVarType = "Integer"
            if self.mPrimaryKey:
                self.WriteMsg("\t@Primary")
                self.WriteMsg('\t@Column(name = "%s", sort = 0, isNotNull = true)' % self.mPrimaryKey)
                for i in self.mDatas:
                    if i[1] == self.mPrimaryKey:
                        pkVarType = self.GetVarType(i[3])
                self.WriteMsg('\tprivate %s %s;' % (pkVarType, utils.convertJavaName(self.mPrimaryKey)))
            idx = 1
            for i in self.mDatas:
                if i[1] == self.mPrimaryKey: continue
                self.WriteMsg('\t@Column(name = "%s", isNotNull = %s, comment = "%s", sort = %d)' 
                        % (i[1], "false" if i[4] == "YES" else "true", i[5], idx))
                self.WriteMsg('\tprivate %s %s;' % (self.GetVarType(i[3]), utils.convertJavaName(i[1])))
                idx += 1
            self.WriteMsg('\n')

            for i in self.mDatas:
                self.WriteMsg('\tpublic %s get%s() {' % (self.GetVarType(i[3]), utils.convertClassName(i[1])))
                self.WriteMsg('\t\treturn %s;' % utils.convertJavaName(i[1]))
                self.WriteMsg('\t}\n')
                self.WriteMsg('\tpublic void set%s(%s %s) {' % (utils.convertClassName(i[1]), self.GetVarType(i[3]), utils.convertJavaName(i[1])))
                self.WriteMsg('\t\tthis.%s = %s;' % (utils.convertJavaName(i[1]), utils.convertJavaName(i[1])))
                self.WriteMsg('\t}\n')

            self.WriteMsg("\t@Override")
            self.WriteMsg("\tpublic String getPirmaryKeyName() {")
            self.WriteMsg('\t\treturn "%s";' % utils.convertJavaName(self.mPrimaryKey))
            self.WriteMsg("\t}\n")
            self.WriteMsg("\t@Override")
            self.WriteMsg('\tpublic %s getPrimaryKeyValue() {' % pkVarType)
            self.WriteMsg('\t\treturn this.%s;' % utils.convertJavaName(self.mPrimaryKey))
            self.WriteMsg("\t}\n")
            self.WriteMsg("\t@Override")
            self.WriteMsg('\tpublic IEntity copy() {')
            self.WriteMsg('\t\t%s entity = new %s();' % (self.mEntityTableName, self.mEntityTableName))
            for i in self.mDatas:
                clsi1 = utils.convertClassName(i[1])
                self.WriteMsg('\t\tentity.set%s(get%s());' % (clsi1, clsi1))
            self.WriteMsg('\t\treturn entity;')
            self.WriteMsg("\t}\n")
            self.WriteMsg("\t@Override")
            self.WriteMsg('\tpublic %s getWebUrlId() {' % pkVarType)
            self.WriteMsg('\t\treturn this.%s;' % utils.convertJavaName(self.mPrimaryKey))
            self.WriteMsg("\t}\n")
            self.WriteMsg("}\n")

    def TryExportService(self):
        dirs = self.CheckDirectory("export")
        fd = os.path.join(dirs, self.cfg["noentity"] + "ExportService.java")
        with open(fd, "w") as of:
            self.mOutPutFileStream = of
            self.WriteMsg(const.JAVA_EXPORT_SVCE_HEADER % (const.PACKAGE_NAME, self.cfg["dirname"]))
            self.WriteMsg("@Component")
            self.WriteMsg("public class %sExportService {" % self.cfg["noentity"])
            self.WriteMsg("\n}\n")

    def TryService(self):
        dirs = self.CheckDirectory("service")
        fd = os.path.join(dirs, self.cfg["noentity"] + "Service.java")
        with open(fd, "w") as of:
            self.mOutPutFileStream = of
            self.WriteMsg(const.JAVA_SERVICE_HEADER % (const.PACKAGE_NAME, self.cfg["dirname"]))
            self.WriteMsg("@Service")
            if self.genType == 1:
                self.WriteMsg("public class %sService extends AbsService<%s, %sDao> {" % (self.cfg["noentity"], self.cfg["entity"], self.cfg["noentity"]))
            else:
                self.WriteMsg("public class %sService {" % self.cfg["noentity"])
            self.WriteMsg("\n}\n")

    def TryGenerateJavaFiles(self):
        self.TryDAO()
        self.TryEasyAction()
        self.TryEntity()
        self.TryExportService()
        self.TryService()

    def LoadTableInfo(self):
        cfg = self.cfg
        db = pymysql.connect(cfg["ip"], cfg["user"], cfg["pass"], cfg["schema"], charset='gbk', port = cfg["port"])
        cursor = db.cursor()
        cursor.execute('''
            SELECT 
                TABLE_NAME,
                COLUMN_NAME,
                COLUMN_KEY,
                DATA_TYPE,
                IS_NULLABLE,
                COLUMN_COMMENT
            FROM
                information_schema.columns
            WHERE
                table_schema = '%s'
                    AND table_name = '%s'
            ''' % (cfg["schema"], cfg["table"]))
        self.mDatas = cursor.fetchall()
        for data in self.mDatas:
            print(data)

    def InitVariables(self):
        self.mTableName = self.cfg["table"]
        entity = self.cfg["entity"]
        self.mEntityTableName = entity
        entityList = list(entity)
        entityList[0] = entityList[0].lower()
        self.mResultMapName = "".join(entityList)
        self.mClassTableName = entity
        # self.mClassTableName = utils.convertClassName(entity)

    def gao(self):
        self.LoadConfig()
        self.LoadTableInfo()
        self.InitVariables()
        self.TryGenerateXMLFile()
        self.TryGenerateJavaFiles()


instance = DataBase2JavaFilesConvertor()


if __name__ == '__main__':
    import sys
    try:
        if int(sys.argv[-1]) == 1:
            instance.setType(1)
        else:
            instance.setType(0)

        instance.gao()
    except:
        traceback.print_exc(5)
    os.system("pause")

