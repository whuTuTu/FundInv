# -*- coding: UTF-8 -*-
"""
@Project :FundInv
@File    :长好短好vs长好短差.py
@IDE     :Pycharm
@Author  :tutu
@Date    :2023/10/31 10:59
柱状图
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
apikey = [config.get("apikey", "ID2"),config.get("apikey", "password2")]
thsLogin = THS_iFinDLogin(apikey[0], apikey[1])
num_pen = 0.1  # 取前num_pen的基金构成指数
n1 = 3  # 近3年
n2 = 1  # 近1年
flag = 'stock'
# ------------------------------------------生成相关时间变量---------------------------------------------------
beginDate = "20141231"  # 开始时间
endDate1 = exchangedate1(endDate)
HYearDate = getHYtime4list(beginDate, lastYearDate)
HYearDate.append(endDate)
print(HYearDate)
# ------------------------------------------以下为代码--------------------------------------------------------
if flag == 'chunzhai':
    # 读取数据
    fundcode4list = getchunzhaicode()
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
    partHYearDate = HYearDate[6::]
    len_time = len(partHYearDate) - 1
    return4list = []
    for i in range(len_time):
        print("------------------------{0}------------------------".format(partHYearDate[i]))
        fundgg4list = gettopnlist(n1, n2, partfundcode4list, NetValueDF, partHYearDate[i], num_pen)  # 长期好，短期好
        fundgb4list = gettopnlist(n1, n2, partfundcode4list, NetValueDF, partHYearDate[i], num_pen,
                                  choice='gb')  # 长期好，短期差
        NetValue = GetbfundnetvalueData(fundcode4list, partHYearDate[i], partHYearDate[i + 1], apikey)  # 获取半年的净值数据
        NetValue.set_index('time', inplace=True)
        fundall = [fundgg4list, fundgb4list]
        types = ['长期好短期好', '长期好短期差']
        linshi4list = []
        for j in range(len(types)):
            fund0 = fundall[j]
            print("{}基金的个数为：{}".format(types[j], len(fund0)))
            df = NetValue[fund0]
            returns_df = df.pct_change()
            weights = [1 / len(returns_df.columns)] * len(returns_df.columns)
            composite_returns = (returns_df * weights).sum(axis=1)
            df[types[j]] = (1 + composite_returns).cumprod()
            linshi4list.append((df[types[j]][-1]-1)*100)
        return4list.append(linshi4list)

    returngg4list = [item[0] for item in return4list]
    returngb4list = [item[1] for item in return4list]
    fig = go.Figure(data=[
        go.Bar(name=types[0], x=partHYearDate[0:-1], y=returngg4list,text=returngg4list,textposition="auto"),
        go.Bar(name=types[1], x=partHYearDate[0:-1], y=returngb4list,text=returngb4list,textposition="auto")
    ])

    # 柱状图模式需要设置：4选1
    fig.update_layout(barmode='group')
    fig.update_layout(title_text='长好短好vs长好短差_纯债版')
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
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
    partHYearDate = HYearDate[6::]
    len_time = len(partHYearDate) - 1
    return4list = []
    for i in range(len_time):
        print("------------------------{0}------------------------".format(partHYearDate[i]))
        fundgg4list = gettopnlist(n1, n2, partfundcode4list, NetValueDF, partHYearDate[i], num_pen)  # 长期好，短期好
        fundgb4list = gettopnlist(n1, n2, partfundcode4list, NetValueDF, partHYearDate[i], num_pen,
                                  choice='gb')  # 长期好，短期差
        NetValue = GetsfundnetvalueData(fundcode4list, partHYearDate[i], partHYearDate[i + 1], apikey)  # 获取半年的净值数据
        NetValue.set_index('time', inplace=True)
        fundall = [fundgg4list, fundgb4list]
        types = ['长期好短期好', '长期好短期差']
        linshi4list = []
        for j in range(len(types)):
            fund0 = fundall[j]
            print("{}基金的个数为：{}".format(types[j], len(fund0)))
            df = NetValue[fund0]
            returns_df = df.pct_change()
            weights = [1 / len(returns_df.columns)] * len(returns_df.columns)
            composite_returns = (returns_df * weights).sum(axis=1)
            df[types[j]] = (1 + composite_returns).cumprod()
            linshi4list.append((df[types[j]][-1]-1)*100)
        return4list.append(linshi4list)

    returngg4list = [item[0] for item in return4list]
    returngb4list = [item[1] for item in return4list]
    fig = go.Figure(data=[
        go.Bar(name=types[0], x=partHYearDate[0:-1], y=returngg4list,text=returngg4list,textposition="auto"),
        go.Bar(name=types[1], x=partHYearDate[0:-1], y=returngb4list,text=returngb4list,textposition="auto")
    ])

    # 柱状图模式需要设置：4选1
    fig.update_layout(barmode='group')
    fig.update_layout(title_text='长好短好vs长好短差_股基版')
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    py_offline.plot(fig, filename='output/StockFund/长好短好vs长好短差_股基版.html')

