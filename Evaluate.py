# -*- coding: UTF-8 -*-
"""
@Project ：FundInv
@File    ：Evaluate.py
@IDE     ：PyCharm
@Author  ：tutu
@Date    ：2023-09-15 14:55
通过计算定量的指标用于基金评价,然后进行排名
"""
# 载入包
import pandas as pd
from iFinDPy import *  # 同花顺API接口
import configparser
from InvokingFunction.GetData import GetbfundnetvalueData, GetindexcloseData, GetsfundnetvalueData
from InvokingFunction.GetGFunction import exchangedate1, getQtime4liet, getHYtime4list, getchunzhaicode, \
    getstockfundcode
from InvokingFunction.GetSFunction import gettopnlist
config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")
# --------------------------------------------全局变量--------------------------------------------------------
beginDate = config.get("time", "beginDate")
endDate = config.get("time", "endDate")
lastYearDate = config.get("time", "lastYearDate")
lastQuarDate = config.get("time", "lastQuarDate")
apikey = [config.get("apikey", "ID1"),config.get("apikey", "password1")]
thsLogin = THS_iFinDLogin(apikey[0], apikey[1])
choice = 'stock'
# ------------------------------------------生成相关时间变量---------------------------------------------------
endDate1 = exchangedate1(endDate)
QuanDate = getQtime4liet(beginDate, lastQuarDate)
YearDate = getHYtime4list(beginDate, lastYearDate)
# ------------------------------------------以下为代码--------------------------------------------------------
if choice == 'stock':
    # 读取数据
    fundcode4list = getstockfundcode()  # 获取纯债基金代码
    print(len(fundcode4list))

    len_time = len(YearDate) - 1
    for i in range(len_time):  # 获取基金净值数据
        NetValue = GetsfundnetvalueData(fundcode4list, YearDate[i], YearDate[i + 1], apikey)
        if i == 0:
            # 纵向拼接
            NetValueDF = NetValue
        else:
            NetValueDF = pd.concat([NetValueDF, NetValue])
    NetValueDF = NetValueDF.drop_duplicates(subset='time', keep='first')
    NetValueDF.set_index('time', inplace=True)

    # 数据缺失值暂时不管
    partfundcode4list = NetValueDF.columns
    n1 = 3  # 近3年
    n2 = 1  # 近1年
    fundgg4list = gettopnlist(n1, n2, partfundcode4list, NetValueDF, endDate, num_pen=1,choice='gg')
    fundggnum4list = range(len(fundgg4list))
    quantitative4df = pd.DataFrame({'thscode':fundgg4list,
                            '总排名':fundggnum4list})
    stockfundlable4df = pd.read_csv("output/StockFund/stockfund_label.csv")
    stockfundlable4df.drop('Unnamed: 0', axis=1, inplace=True)
    quantitative4df = pd.merge(quantitative4df, stockfundlable4df, on='thscode', how='left')
    quantitative4df = quantitative4df.sort_values(by='总排名')
    quantitative4df.to_csv("output/StockFund/quantitative.csv")

    # 读取数据
    fundcode4list = getstockfundcode()  # 获取纯债基金代码
    print(len(fundcode4list))

if choice == 'chunzhai':
    fundcode4list = getchunzhaicode()  # 获取纯债基金代码
    print(len(fundcode4list))
    len_time = len(YearDate) - 1
    for i in range(len_time):  # 获取基金净值数据
        NetValue = GetbfundnetvalueData(fundcode4list, YearDate[i], YearDate[i + 1], apikey)
        if i == 0:
            # 纵向拼接
            NetValueDF = NetValue
        else:
            NetValueDF = pd.concat([NetValueDF, NetValue])
    NetValueDF = NetValueDF.drop_duplicates(subset='time', keep='first')
    NetValueDF.set_index('time', inplace=True)

    # 数据缺失值暂时不管
    partfundcode4list = NetValueDF.columns
    n1 = 3  # 近3年
    n2 = 1  # 近1年
    fundgg4list = gettopnlist(n1, n2, partfundcode4list, NetValueDF, endDate, num_pen=1,choice='gg')
    fundggnum4list = range(len(fundgg4list))
    quantitative4df = pd.DataFrame({'thscode':fundgg4list,
                                    '总排名':fundggnum4list})
    stockfundlable4df = pd.read_csv("output/ChunzhaiFund/chunzhai_label.csv")
    stockfundlable4df.drop('Unnamed: 0', axis=1, inplace=True)
    quantitative4df = pd.merge(quantitative4df, stockfundlable4df, on='thscode', how='left')
    quantitative4df = quantitative4df.sort_values(by='总排名')
    quantitative4df.to_csv("output/ChunzhaiFund/quantitative.csv")