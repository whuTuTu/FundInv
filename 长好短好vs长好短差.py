# -*- coding: UTF-8 -*-
"""
@Project :FundInv
@File    :长好短好vs长好短差.py
@IDE     :Pycharm
@Author  :tutu
@Date    :2023/10/31 10:59
"""
# 载入包
import pandas as pd
import configparser
from iFinDPy import *  # 同花顺API接口
from InvokingFunction.GetData import GetbfundnetvalueData, GetsfundnetvalueData
from InvokingFunction.GetGFunction import exchangedate1, getHYtime4list, getchunzhaicode, getstockfundcode
from InvokingFunction.GetSFunction import gettopnlist, returndf2fig, indexreturn2quantitative
import plotly.graph_objects as go
import plotly.offline as py_offline
import matplotlib.pyplot as plt
config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")
# --------------------------------------------全局变量--------------------------------------------------------
endDate = config.get("time", "endDate")
lastYearDate = config.get("time", "lastYearDate")
lastQuarDate = config.get("time", "lastQuarDate")
apikey = [config.get("apikey", "ID1"),config.get("apikey", "password1")]
thsLogin = THS_iFinDLogin(apikey[0], apikey[1])
num_pen = 0.1  # 取前num_pen的基金构成指数
n1 = 3  # 近3年
n2 = 1  # 近1年
flag = 'stock'
# ------------------------------------------生成相关时间变量---------------------------------------------------
beginDate = "20180101"  # 开始时间
endDate1 = exchangedate1(endDate)
HYearDate = getHYtime4list(beginDate, lastYearDate)
HYearDate.append(endDate)
print(HYearDate)
# ------------------------------------------以下为代码--------------------------------------------------------
if flag == 'chunzhai':
    # 读取数据
    fundcode4list = getchunzhaicode()  # 获取纯债基金代码
    len_time = len(HYearDate) - 1
    for i in range(len_time):  # 获取基金净值数据
        NetValue = GetbfundnetvalueData(fundcode4list, HYearDate[i], HYearDate[i + 1], apikey)
        if i == 0:
            # 纵向拼接
            NetValueDF = NetValue
        else:
            NetValueDF = pd.concat([NetValueDF, NetValue])
    NetValueDF = NetValueDF.drop_duplicates(subset='time', keep='first')
    NetValueDF.set_index('time', inplace=True)
    partfundcode4list = NetValueDF.columns
    print(NetValueDF.head())

    partHYearDate = HYearDate[-6::]
    print(partHYearDate)

    len_time = len(partHYearDate) - 1
    for i in range(len_time):
        print("------------------------{0}------------------------".format(partHYearDate[i]))
        fundgg4list = gettopnlist(n1, n2, partfundcode4list, NetValueDF, partHYearDate[i], num_pen)  # 长期好，短期好
        fundgb4list = gettopnlist(n1, n2, partfundcode4list, NetValueDF, partHYearDate[i], num_pen, choice='gb')  # 长期好，短期差
        NetValue = GetbfundnetvalueData(fundcode4list, partHYearDate[i], partHYearDate[i + 1], apikey)  # 获取半年的净值数据
        NetValue.set_index('time', inplace=True)
        fundall = [fundgg4list,fundgb4list]
        types = ['长期好短期好', '长期好短期差']
        for j in range(len(types)):
            fund0 = fundall[j]
            print("{}基金的个数为：{}".format(types[j], len(fund0)))
            df = NetValue[fund0]
            returns_df = df.pct_change()
            weights = [1 / len(returns_df.columns)] * len(returns_df.columns)
            composite_returns = (returns_df * weights).sum(axis=1)
            df[types[j]] = (1 + composite_returns).cumprod()
            if i == 0:
                # 除了第一块数据，其余都要乘以上一块的最后一排数字
                pass
            else:
                df[types[j]] = df[types[j]] * lastnet[j]

            if j == 0:
                # 横向拼接
                Return = df[[types[j]]]
            else:
                Return = pd.concat([Return, df[[types[j]]]], axis=1)

        if i == 0:
            # 纵向拼接
            ReturnDF = Return
        else:
            ReturnDF = pd.concat([ReturnDF, Return])
        lastnet = Return.iloc[-1].tolist()
    fig = returndf2fig(ReturnDF)
    py_offline.plot(fig, filename='output/ChunzhaiFund/长好短好vs长好短差_纯债版.html')

if flag == 'stock':
    # 读取数据
    fundcode4list = getstockfundcode()
    len_time = len(HYearDate) - 1
    for i in range(len_time):  # 获取基金净值数据
        NetValue = GetsfundnetvalueData(fundcode4list, HYearDate[i], HYearDate[i + 1], apikey)
        if i == 0:
            # 纵向拼接
            NetValueDF = NetValue
        else:
            NetValueDF = pd.concat([NetValueDF, NetValue])
    NetValueDF = NetValueDF.drop_duplicates(subset='time', keep='first')
    NetValueDF.set_index('time', inplace=True)
    partfundcode4list = NetValueDF.columns
    partHYearDate = HYearDate[-6::]
    len_time = len(partHYearDate) - 1
    for i in range(len_time):
        print("------------------------{0}------------------------".format(partHYearDate[i]))
        fundgg4list = gettopnlist(n1, n2, partfundcode4list, NetValueDF, partHYearDate[i], num_pen)  # 长期好，短期好
        fundgb4list = gettopnlist(n1, n2, partfundcode4list, NetValueDF, partHYearDate[i], num_pen,
                                  choice='gb')  # 长期好，短期差
        NetValue = GetsfundnetvalueData(fundcode4list, partHYearDate[i], partHYearDate[i + 1], apikey)  # 获取半年的净值数据
        NetValue.set_index('time', inplace=True)
        fundall = [fundgg4list, fundgb4list]
        types = ['长期好短期好', '长期好短期差']
        for j in range(len(types)):
            fund0 = fundall[j]
            print("{}基金的个数为：{}".format(types[j], len(fund0)))
            df = NetValue[fund0]
            returns_df = df.pct_change()
            weights = [1 / len(returns_df.columns)] * len(returns_df.columns)
            composite_returns = (returns_df * weights).sum(axis=1)
            df[types[j]] = (1 + composite_returns).cumprod()
            if i == 0:
                # 除了第一块数据，其余都要乘以上一块的最后一排数字
                pass
            else:
                df[types[j]] = df[types[j]] * lastnet[j]

            if j == 0:
                # 横向拼接
                Return = df[[types[j]]]
            else:
                Return = pd.concat([Return, df[[types[j]]]], axis=1)

        if i == 0:
            # 纵向拼接
            ReturnDF = Return
        else:
            ReturnDF = pd.concat([ReturnDF, Return])
        lastnet = Return.iloc[-1].tolist()
    fig = returndf2fig(ReturnDF)
    py_offline.plot(fig, filename='output/StockFund/长好短好vs长好短差_股基版.html')



