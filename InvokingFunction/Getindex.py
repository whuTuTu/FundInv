# -*- coding: UTF-8 -*-
"""
@Project ：FundInv
@File    ：index.py
@IDE     ：PyCharm
@Author  ：tutu
@Date    ：2023-08-24 10:29
定期跟踪指数
"""
# 载入包
import pandas as pd
from iFinDPy import *  # 同花顺API接口
import time
import configparser
import plotly.offline as py_offline
import matplotlib.pyplot as plt
import os
from InvokingFunction.GetData import GetsfundnetvalueData, GetbfundnetvalueData
from InvokingFunction.GetGFunction import exchangedate1, getQtime4liet, getHYtime4list, getstockfundcode, \
    getchunzhaicode
import warnings
from InvokingFunction.GetShortbondfundLabel import getbondtype
from InvokingFunction.GetShortstockfundLabel import getstyle, getindustry
from InvokingFunction.Short2Long import Getstockfund4Long

warnings.filterwarnings(action='ignore')
warnings.filterwarnings(action='ignore')  # 导入warnings模块，并指定忽略代码运行中的警告信息
plt.rcParams['font.sans-serif'] = ['SimHei']  # 解决中文显示乱码的问题
plt.rcParams['axes.unicode_minus'] = False
start = time.perf_counter()  # 代码开始的时间
config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")
path = "D:\TFCode\FundInv"
os.chdir(path)
# --------------------------------------------全局变量--------------------------------------------------------
endDate = config.get("time", "endDate")
lastYearDate = config.get("time", "lastYearDate")
lastQuarDate = config.get("time", "lastQuarDate")
beginDate = config.get("time", "beginDate")
apikey = [config.get("apikey", "ID1"), config.get("apikey", "password1")]
thsLogin = THS_iFinDLogin(apikey[0], apikey[1])


def getindex(flag,yesend = True, beginDate=beginDate, lastQuarDate=lastQuarDate, lastYearDate=lastYearDate, endDate=endDate):
    """

    :param flag: 1-股基行业；2-行业均衡性股基的风格；3-债基的利率信用分类
    :param beginDate:
    :param lastQuarDate:
    :param lastYearDate:
    :param endDate:
    :return:
    """
    # ------------------------------------------生成相关时间变量--------------------------------------------------------
    QuanDate = getQtime4liet(beginDate, lastQuarDate)
    HYearDate = getHYtime4list(beginDate, lastYearDate)
    if yesend == True:
        QuanDate.append(endDate)
        HYearDate.append(endDate)
    else:
        pass
    # ------------------------------------------以下为代码-------------------------------------------------------------
    if flag == 1:
        fundcode4list = getstockfundcode()  # 获取股票基金代码
        len_time = len(HYearDate) - 1
        for i in range(len_time):
            MyFundDF = getindustry(HYearDate[i], apikey)
            NetValue = GetsfundnetvalueData(fundcode4list, HYearDate[i], HYearDate[i + 1], apikey)  # 获取半年的净值数据
            NetValue.set_index('time', inplace=True)
            # 分类基金
            types = ['周期行业基金', '医药行业基金', '制造行业基金', '金融地产行业基金', 'TMT行业基金', '消费行业基金',
                     '行业均衡基金']
            for j in range(len(types)):
                fund0 = MyFundDF[MyFundDF['INDtype'] == types[j]].iloc[:, [0]].values.tolist()
                fund0 = [item for sublist in fund0 for item in sublist]
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

    if flag == 2:
        fundcode4list = getstockfundcode()  # 获取股票基金代码
        len_time = len(HYearDate) - 1
        for i in range(len_time):
            indlong4df = Getstockfund4Long(HYearDate[-1], lastQuarDate, apikey, flag=1)
            styleshort4df = getstyle(HYearDate[i], apikey)
            MyFundDF = pd.merge(indlong4df, styleshort4df, on='thscode', how='left')  # 合并数据
            NetValue = GetsfundnetvalueData(fundcode4list, HYearDate[i], HYearDate[i + 1], apikey)  # 获取半年的净值数据
            NetValue.set_index('time', inplace=True)

            # 分类基金
            MyFundDF = MyFundDF[MyFundDF['行业标签'] == '稳定行业均衡基金']
            types = ['均衡型', '成长型', '价值型', '成长-均衡型', '均衡-价值型']
            for j in range(len(types)):
                fund0 = MyFundDF[MyFundDF['Xstyle'] == types[j]].iloc[:, [0]].values.tolist()
                fund0 = [item for sublist in fund0 for item in sublist]
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

    if flag == 3:
        fundcode4list = getchunzhaicode()
        len_time = len(HYearDate) - 1
        for i in range(len_time):
            MyFundDF = getbondtype(QuanDate[i], apikey)
            NetValue = GetbfundnetvalueData(fundcode4list, HYearDate[i], HYearDate[i + 1], apikey)  # 获取半年的净值数据
            NetValue.set_index('time', inplace=True)
            partfundcode4list = NetValue.columns
            MyFundDF = MyFundDF[MyFundDF['thscode'].isin(partfundcode4list)]

            # 分类基金
            # types = ['信用债', '利率债']
            types = ['信用债']
            print(types)
            for j in range(len(types)):
                fund0 = MyFundDF[MyFundDF['bondfundtype'] == types[j]].iloc[:, [0]].values.tolist()
                fund0 = [item for sublist in fund0 for item in sublist]
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

    ReturnDF1 = ReturnDF.reset_index()
    ReturnDF1 = ReturnDF1.drop_duplicates(subset='time', keep='first')
    ReturnDF1.set_index('time', inplace=True)
    return ReturnDF1
