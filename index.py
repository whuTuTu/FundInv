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
from InvokingFunction.GetData import GetsfundnetvalueData, GetbfundnetvalueData
from InvokingFunction.GetGFunction import exchangedate1, getQtime4liet, getHYtime4list, getstockfundcode, \
    getchunzhaicode
import warnings
from InvokingFunction.GetSFunction import indexreturn2quantitative, returndf2fig
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
# --------------------------------------------全局变量--------------------------------------------------------
endDate = config.get("time", "endDate")
lastYearDate = config.get("time", "lastYearDate")
lastQuarDate = config.get("time", "lastQuarDate")
apikey = [config.get("apikey", "ID2"),config.get("apikey", "password2")]

thsLogin = THS_iFinDLogin(apikey[0], apikey[1])
style_flag = True
ind_flag = True
types_flag = True

# ------------------------------------------生成相关时间变量--------------------------------------------------------
beginDate = "20221231"  # 开始时间
QuanDate = getQtime4liet(beginDate, lastQuarDate)
HYearDate = getHYtime4list(beginDate, lastYearDate)
QuanDate.append(endDate)
HYearDate.append(endDate)
# ------------------------------------------以下为代码-------------------------------------------------------------
if ind_flag:
    fundcode4list = getstockfundcode()  # 获取股票基金代码
    len_time = len(HYearDate) - 1
    for i in range(len_time):
        print("------------------------{0}------------------------".format(HYearDate[i]))
        MyFundDF = getindustry(HYearDate[i], apikey)
        NetValue = GetsfundnetvalueData(fundcode4list, HYearDate[i], HYearDate[i + 1], apikey)  # 获取半年的净值数据
        NetValue.set_index('time', inplace=True)

        # 分类基金
        types = ['周期行业基金', '医药行业基金', '制造行业基金', '金融地产行业基金', 'TMT行业基金', '消费行业基金', '其他行业基金', '行业均衡基金']
        for j in range(len(types)):
            fund0 = MyFundDF[MyFundDF['INDtype'] == types[j]].iloc[:, [0]].values.tolist()
            fund0 = [item for sublist in fund0 for item in sublist]
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
    fig.update_layout(title_text='行业指数')
    py_offline.plot(fig, filename='output/StockFund/行业指数.html')
    quantitative4df = indexreturn2quantitative(types, ReturnDF)
    quantitative4df.to_csv('output/StockFund/行业指数指标'+endDate+'.csv')

if style_flag:
    fundcode4list = getstockfundcode()  # 获取股票基金代码
    len_time = len(HYearDate) - 1
    for i in range(len_time):
        print("------------------------{0}------------------------".format(HYearDate[i]))
        indlong4df = Getstockfund4Long(HYearDate[i], lastQuarDate, apikey, flag=1)
        styleshort4df = getstyle(HYearDate[i], apikey)
        MyFundDF = pd.merge(indlong4df, styleshort4df, on='thscode', how='left')  # 合并数据
        NetValue = GetsfundnetvalueData(fundcode4list, HYearDate[i], HYearDate[i + 1], apikey)  # 获取半年的净值数据
        NetValue.set_index('time', inplace=True)

        # 分类基金
        MyFundDF = MyFundDF[MyFundDF['行业标签'] == '稳定行业均衡基金']
        types = ['均衡型','成长型','价值型','成长-均衡型','均衡-价值型']
        for j in range(len(types)):
            fund0 = MyFundDF[MyFundDF['Xstyle'] == types[j]].iloc[:, [0]].values.tolist()
            fund0 = [item for sublist in fund0 for item in sublist]
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
    fig.update_layout(title_text='风格指数')
    py_offline.plot(fig, filename='output/StockFund/风格指数.html')
    quantitative4df = indexreturn2quantitative(types, ReturnDF)
    quantitative4df.to_csv("output/StockFund/风格指数指标"+endDate+".csv")

if types_flag:
    fundcode4list = getchunzhaicode()
    print(len(fundcode4list))
    len_time = len(HYearDate) - 1
    for i in range(len_time):
        print("------------------------{0}------------------------".format(HYearDate[i]))
        MyFundDF = getbondtype(HYearDate[i], apikey)
        NetValue = GetbfundnetvalueData(fundcode4list, HYearDate[i], HYearDate[i + 1], apikey)  # 获取半年的净值数据
        NetValue.set_index('time', inplace=True)

        # 分类基金
        types = ['信用债', '利率债']
        print(types)
        for j in range(len(types)):
            fund0 = MyFundDF[MyFundDF['bondfundtype'] == types[j]].iloc[:, [0]].values.tolist()
            fund0 = [item for sublist in fund0 for item in sublist]
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
    fig.update_layout(title_text='债券种类指数')
    py_offline.plot(fig, filename='output/ChunzhaiFund/债券种类指数.html')
    quantitative4df = indexreturn2quantitative(types, ReturnDF)
    quantitative4df.to_csv("output/ChunzhaiFund/债券种类指数指标"+endDate+".csv")






