# -*- coding: UTF-8 -*-
"""
@Project ：FundInv 
@File    ：SUNTIME.py
@IDE     ：PyCharm 
@Author  ：tutu
@Date    ：2023-08-21 9:44
尝试朝阳永续私募数据库的连接,常出现连接失败的情况，多跑几次
有两种，用pymysql或者创造engine
"""
# 法一
import pymysql
import pandas as pd
# 连接数据库
conn = pymysql.connect(
    host='106.75.45.237',  # 连接名称，默认127.0.0.1
    user='simu4_tfzqzj',  # 用户名
    passwd='suO9A2nfTBXS2NRV',  # 密码
    port=50128,  # 端口，默认为3306
    db='CUS_FUND_DB',  # 数据库名称
    charset='utf8',  # 字符编码
)
cursor = conn.cursor()

sql = "SELECT fund_id,fund_full_name,foundation_date FROM t_fund_info WHERE fund_full_name LIKE '%光大阳光%' ORDER BY foundation_date DESC"
cursor.execute(sql)
pdate = pd.read_sql(sql, conn)  # 以DataFrame格式读取显示
print(pdate)
conn.close()

# 法二
# import pandas as pd
# from sqlalchemy import create_engine
# # 创建 SQLAlchemy 数据库连接引擎
# engine = create_engine('mysql+pymysql://simu4_tfzqzj:suO9A2nfTBXS2NRV@106.75.45.237:50128/CUS_FUND_DB')
# # 使用连接引擎读取数据
# sql_query = "SELECT fund_id,fund_full_name,foundation_date " \
#             "FROM t_fund_info " \
#             "WHERE fund_full_name LIKE '%%光大阳光%%' " \
#             "ORDER BY foundation_date DESC "
# df = pd.read_sql(sql_query, engine)
# # 打印读取的数据
# print(df)
