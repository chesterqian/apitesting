# -*- coding: UTF-8 -*-
import re

import pymysql


class MySqlHandler(object):
    """
    操作mysql数据库，基本方法
    """

    def __init__(self, host="localhost", username="root", password="", port=3306, database="test"):
        self.host = host
        self.username = username
        self.password = password
        self.database = database
        self.port = port
        self.connection = None
        self.cursor = None

        try:
            self.connection = pymysql.connect(host=self.host, user=self.username, passwd=self.password, port=self.port,
                                              db=self.database, charset='utf8')
            self.cursor = self.connection.cursor()
        except Exception as e:
            print("DataBase connect error,please check the db config:%s" % e)

    def close(self):
        """
        关闭数据库连接
        """
        if not self.connection:
            self.connection.close()

    def get_version(self):
        """
        获取数据库的版本号
        """
        return self.get_one_data("select version()")

    def get_one_data(self, sql):
        try:
            self.cursor.execute(sql)
            record = self.cursor.fetchone()
            return record
        except pymysql.Error as e:
            print('MySQL execute failed! ERROR (%s): %s' % (e.args[0], e.args[1]))
            return None

    def get_all_data(self, sql):
        return self.execute_sql(sql)

    def creat_table(self, tablename, attr_dict, constraint):
        """
        创建数据库表
        :param tablename: 表名字
        :param attr_dict: 属性键值对,{'book_name':'varchar(200) NOT NULL'...}
        :param constraint: 主外键约束,PRIMARY KEY(`id`)
        :return:
        """
        if self.is_table_exist(tablename):
            return
        sql = ''
        sql_mid = '`id` bigint(11) NOT NULL AUTO_INCREMENT,'
        for attr, value in attr_dict.items():
            sql_mid = sql_mid + '`' + attr + '`' + ' ' + value + ','
        sql = sql + 'CREATE TABLE IF NOT EXISTS %s (' % tablename
        sql = sql + sql_mid
        sql = sql + constraint
        sql = sql + ') ENGINE=InnoDB DEFAULT CHARSET=utf8'
        print('creatTable:' + sql)
        self.execute_commit(sql)

    def execute_sql(self, sql=''):
        """
        执行sql语句，针对读操作返回结果集
        """
        try:
            self.cursor.execute(sql)
            records = self.cursor.fetchall()
            return records
        except pymysql.Error as e:
            print('MySQL execute failed! ERROR (%s): %s' % (e.args[0], e.args[1]))
            return None

    def execute_commit(self, sql=''):
        """
        执行数据库sql语句，针对更新,删除,事务等操作失败时回滚
        """
        try:
            self.cursor.execute(sql)
            self.connection.commit()
        except pymysql.Error as e:
            self.connection.rollback()
            error = 'MySQL execute failed! ERROR (%s): %s' % (e.args[0], e.args[1])
            print("error:%s" % error)
            return error

    def insert(self, tablename, params):
        """
        创建数据库表
        :param tablename: ：表名字
        :param params: ：属性键 - 属性值
        """

        keys = []
        values = []

        for tmp_key, tmp_value in params.items():
            keys.append(tmp_key)
            if isinstance(tmp_value, str):
                values.append("\'" + tmp_value + "\'")
            else:
                values.append(tmp_value)

        attrs_sql = '(' + ','.join(keys) + ')'
        values_sql = ' values(' + ','.join(values) + ')'
        sql = 'insert into %s' % tablename
        sql = sql + attrs_sql + values_sql
        print('_insert:' + sql)
        self.execute_commit(sql)

    def select(self, tablename, condition_dict='', order='', fields='*'):
        """
        查询数据
        :param tablename: 表名字
        :param condition_dict: 查询条件
        :param order: 排序条件
        :param fields:
        :return:

        example：
                print mydb.select(table)
                print mydb.select(table, fields=["name"])
                print mydb.select(table, fields=["name", "age"])
                print mydb.select(table, fields=["age", "name"])
        """
        condition_sql = ' '
        if condition_dict != '':
            for k, v in condition_dict.items():
                condition_sql = condition_sql + k + '=' + v + ' and'
        condition_sql = condition_sql + ' 1=1 '

        if fields == "*":
            sql = 'select * from %s where ' % tablename
        else:
            if isinstance(fields, list):
                fields = ",".join(fields)
                sql = 'select %s from %s where ' % (fields, tablename)
            else:
                print("fields input error, please input list fields.")

        sql = sql + condition_sql + order
        print('select:' + sql)
        return self.execute_sql(sql)

    def insert_many(self, tablename, attrs, values):
        """
        插入多条数据
        :param tablename:表名字
        :param attrs:属性键
        :param values:属性值

        example：
            table='test_mysqldb'
            key = ["id" ,"name", "age"]
            value = [[101, "liuqiao", "25"], [102,"liuqiao1", "26"], [103 ,"liuqiao2", "27"], [104 ,"liuqiao3", "28"]]
            mydb.insertMany(table, key, value)
        """
        values_sql = ['%s' for v in attrs]
        attrs_sql = '(' + ','.join(attrs) + ')'
        values_sql = ' values(' + ','.join(values_sql) + ')'
        sql = 'insert into %s' % tablename
        sql = sql + attrs_sql + values_sql
        print('insert_many:' + sql)

        try:
            for i in range(0, len(values), 20000):
                self.cursor.executemany(sql, values[i:i + 20000])
                self.connection.commit()
        except pymysql.Error as e:
            self.connection.rollback()
            print('insert_many execute failed! ERROR (%s): %s' % (e.args[0], e.args[1]))

    def delete(self, tablename, condition_dict):
        """
        删除数据
        :param tablename：表名字
        :param condition_dict：删除条件字典

        example：
            params = {"name" : "caixinglong", "age" : "38"}
            mydb.delete(table, params)
        """
        conditon_sql = ' '
        if condition_dict != '':
            for k, v in condition_dict.items():
                if isinstance(v, str):
                    v = "\'" + v + "\'"
                conditon_sql = conditon_sql + tablename + "." + k + '=' + v + ' and '
        conditon_sql = conditon_sql + ' 1=1 '

        sql = "delete from %s where%s" % (tablename, conditon_sql)
        print(sql)
        return self.execute_commit(sql)

    def update(self, tablename, attrs_dict, conditon_dict):
        """
        更新数据
        args：
        :param tablename：表名字
        :param attrs_dict：更新属性键值对字典
        :param conditon_dict：更新条件字典

        example：
            params = {"name" : "caixinglong", "age" : "38"}
            cond_dict = {"name" : "liuqiao", "age" : "18"}
            mydb.update(table, params, cond_dict)

        """
        attrs_list = []
        conditon_sql = ' '
        for tmp_key, tmp_value in attrs_dict.items():
            attrs_list.append("`" + tmp_key + "`" + "=" + "\'" + tmp_value + "\'")
        attrs_sql = ",".join(attrs_list)
        print("attrs_sql:", attrs_sql)

        if conditon_dict != '':
            for k, v in conditon_dict.items():
                if isinstance(v, str):
                    v = "\'" + v + "\'"
                conditon_sql = conditon_sql + "`" + tablename + "`." + "`" + k + "`" + '=' + v + ' and '
        conditon_sql = conditon_sql + ' 1=1 '

        sql = "update %s set %s where%s" % (tablename, attrs_sql, conditon_sql)
        print(sql)
        return self.execute_commit(sql)

    def drop_table(self, tablename):
        """
        删除数据库表
        :param tablename：表名字
        """
        sql = "drop table  %s" % tablename
        self.execute_commit(sql)

    def delete_table(self, tablename):
        """
        清空数据库表
        :param tablename：表名字
        """
        sql = "delete from %s" % tablename
        self.execute_commit(sql)

    def is_table_exist(self, tablename):
        """
        判断数据表是否存在
        :param tablename: 表名字
        :return: 存在返回True，不存在返回False
        """
        sql = "select * from %s" % tablename
        result = self.execute_commit(sql)

        if result is None:
            return True
        else:
            if re.search("doesn't exist", result):
                return False
            else:
                return True

    def get_datas_by_sqlfile(self, sql_file, params_list):
        """
         execute sql file and return records
        :param sql_file:
        :param params_list: tuple or tuple list
        :return:
        """

        out_list, content, sqls = [], None, None

        with open(sql_file, 'r', encoding='utf-8') as handle:
            content = handle.read()

        if not isinstance(params_list, list):
            params_list = [params_list]

        for params in params_list:
            content = content % params

            sqls = content.split(';')[:-1]
            sqls = [x.replace('\n', ' ') for x in sqls]

            for index in range(len(sqls)):
                records = self.execute_sql(sqls[index])
                if index == len(sqls) - 1 and records:
                    out_list.append(records)

        return out_list
