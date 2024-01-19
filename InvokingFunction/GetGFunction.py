# -*- coding: UTF-8 -*-
"""
@Project ：FundInv
@File    ：GetGFunction.py
@IDE     ：PyCharm
@Author  ：tutu
@Date    ：2023-09-15 14:46
用于储存一些乱七八糟的函数，例如数据格式转换什么的
"""
# 载入包
import pandas as pd


def exchangedate1(YearDate):
    """
    将20200101变成2020-01-01
    :param YearDate:
    :return:
    """
    return YearDate[0:4] + '-' + YearDate[4:6] + '-' + YearDate[6::]

def df2list(df1):
    """
    将pd的第一列df.iloc[:,[0]]变成list
    :param df1:
    :return: list
    """
    fund0 = df1.iloc[:, [0]].values.tolist()
    fund0 = [item for sublist in fund0 for item in sublist]
    return fund0

def getchunzhaicode():
    """
    【纯债基金代码】读文件获取筛选后的基金代码，输出list
    :return:list
    """
    cunzhai4df = pd.read_csv("output/ChunzhaiFund/chunzhai_filter.csv")
    cunzhai4df.drop('Unnamed: 0', axis=1, inplace=True)
    return df2list(cunzhai4df.iloc[:, [0]])

def getstockfundcode():
    """
    【股票基金代码】读文件获取筛选后的基金代码，输出list
    :return:list
    """
    MyFundDF = pd.read_csv("output/StockFund/stockfund_filter.csv")
    MyFundDF.drop('Unnamed: 0', axis=1, inplace=True)
    return df2list(MyFundDF.iloc[:, [0]])

def getHYtime4list(beginDate, lastYearDate):
    """
    获取半年度频率时间节点
    :param beginDate:
    :param lastYearDate:
    :return:
    """
    beginyear = beginDate[0:4]
    endyear = lastYearDate[0:4]
    monthday = ['0630', '1231']
    aRepDate = [str(i) + j for i in range(int(beginyear), int(endyear) + 1) for j in monthday]
    repDateY = []
    for i in aRepDate:
        if lastYearDate >= i >= beginDate:
            repDateY.append(i)
        else:
            continue
    return repDateY
def getYtime4list(beginDate, lastYearDate):
    """
    获取半年度频率时间节点
    :param beginDate:
    :param lastYearDate:
    :return:
    """
    beginyear = beginDate[0:4]
    endyear = lastYearDate[0:4]
    monthday = '1231'
    aRepDate = [str(i) + j for i in range(int(beginyear), int(endyear) + 1) for j in monthday]
    repDateY = []
    for i in aRepDate:
        if lastYearDate >= i >= beginDate:
            repDateY.append(i)
        else:
            continue
    return repDateY

def getQtime4liet(beginDate, lastQuarDate):
    """
    获取季度频率时间节点
    :param beginDate:
    :param lastQuarDate:
    :return:
    """
    beginyear = beginDate[0:4]
    endyear = lastQuarDate[0:4]
    monthday = ['0331', '0630', '0930', '1231']
    aRepDate = [str(i) + j for i in range(int(beginyear), int(endyear) + 1) for j in monthday]
    repDateQ = []
    for i in aRepDate:
        if lastQuarDate >= i >= beginDate:
            repDateQ.append(i)
        else:
            continue
    return repDateQ








