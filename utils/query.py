from pymysql import *

conn = connect(host='localhost',user='root',password='123456',database='job',port=3306)
cursor = conn.cursor()


def querys(sql,params,type='no_select'):
    params = tuple(params)
    cursor.execute(sql,params)
    if type != 'no_select':
        data_list = cursor.fetchall()
        conn.commit()
        return data_list
    else:
        conn.commit()
        return '数据库语句执行成功'

"""
这段代码是用来连接MySQL数据库并执行查询语句的。
第 1 行：从 pymysql 库中导入 connect 方法。
第 3-8 行：连接 MySQL 数据库，需要指定主机名、用户名、密码、数据库名和端口号，连接成功后返回连接对象 conn。
第 9 行：创建游标对象 cursor。
第 11-15 行：定义了一个函数 querys，接收三个参数：sql，params，type。sql 是要执行的 SQL 查询语句，params 是一个元组类型的参数，用于填充查询语句中的占位符，type 是执行的 SQL 语句类型，如果是查询语句，则返回查询结果，否则返回 '数据库语句执行成功'。
第 16 行：将 params 转换为元组类型。
第 17 行：使用 cursor 对象执行 SQL 查询语句，并使用 params 替换 SQL 语句中的占位符。
第 18-20 行：如果查询语句不是 'no_select'，则获取所有查询结果并返回；否则，提交事务并返回 '数据库语句执行成功'。
"""