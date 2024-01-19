# -*- coding: UTF-8 -*-
"""
@Project ：FundInv
@File    ：FundSum.py
@IDE     ：PyCharm
@Author  ：tutu
@Date    ：2023-10-10 16:38
半年更新
"""
import pandas as pd
import time
import matplotlib.pyplot as plt
import configparser
from InvokingFunction.BondfundFirstfilter import BondFirstFilter
from InvokingFunction.GetShortbondfundLabel import getdingkai
from InvokingFunction.StockfundFirstfilter import StockFirstFilter
from InvokingFunction.Short2Long import Getstockfund4Long, Getbondfund4Long
import warnings
warnings.filterwarnings(action='ignore')  # 导入warnings模块，并指定忽略代码运行中的警告信息
plt.rcParams['font.sans-serif'] = ['SimHei']  # 解决中文显示乱码的问题
plt.rcParams['axes.unicode_minus'] = False

start = time.perf_counter()  # 代码开始的时间
config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")
# 　------------------------------------------全局变量--------------------------------------------------------

endDate = config.get("time", "endDate")
lastYearDate = config.get("time", "lastYearDate")
lastQuarDate = config.get("time", "lastQuarDate")
apikey = [config.get("apikey", "ID2"),config.get("apikey", "password2")]
choice = 'bond'

# ------------------------------------------以下为代码--------------------------------------------------------
if choice == 'stock':
    print("——————————————————————————————————第一次筛选———————————————————————————————————————")
    stockfund4df = StockFirstFilter(endDate, apikey)
    print("第一次筛选运行时间：", time.perf_counter() - start, "秒")

    print("——————————————————————————————————获取行业主题标签——————————————————————————————")
    Ind4df = Getstockfund4Long(lastYearDate, lastYearDate, apikey, 1)
    print("获取行业主题标签运行时间：", time.perf_counter() - start, "秒")

    print("——————————————————————————————————获取大小盘标签——————————————————————————————")
    marketvalue4df = Getstockfund4Long(lastYearDate, lastYearDate, apikey, 2)
    print("获取大小盘标签运行时间：", time.perf_counter() - start, "秒")

    print("——————————————————————————————————获取风格标签——————————————————————————————")
    style4df = Getstockfund4Long(lastYearDate, lastYearDate, apikey, 3)
    print("获取风格标签运行时间：", time.perf_counter() - start, "秒")

    print("——————————————————————————————————获取共振因子标签———————————————————————————————————")
    h4df = Getstockfund4Long(lastQuarDate, lastQuarDate, apikey, 4)
    print("获取共振因子标签运行时间：", time.perf_counter() - start, "秒")

    print("——————————————————————————————————获取集中度标签———————————————————————————————————")
    cr4df = Getstockfund4Long(lastQuarDate, lastQuarDate, apikey, 5)
    print("获取集中度标签运行时间：", time.perf_counter() - start, "秒")

    # 合并数据
    stockfund4df = pd.merge(stockfund4df, Ind4df, on='thscode', how='left')
    stockfund4df = pd.merge(stockfund4df, marketvalue4df, on='thscode', how='left')
    stockfund4df = pd.merge(stockfund4df, style4df, on='thscode', how='left')
    stockfund4df = pd.merge(stockfund4df, h4df, on='thscode', how='left')
    stockfund4df = pd.merge(stockfund4df, cr4df, on='thscode', how='left')
    stockfund4df.to_csv("output/Stockfund/stockfund_label.csv")

    for item in ['行业标签', '大小盘标签', '风格标签', '共振因子标签', '集中度标签']:
        types = stockfund4df[item].dropna().unique().tolist()
        for i in range(len(types)):
            fund0 = stockfund4df[stockfund4df[item] == types[i]]
            print("{}基金的个数为：{}".format(types[i], len(fund0)))

if choice == 'bond':
    print("——————————————————————————————————第一次筛选———————————————————————————————————————")
    stockfund4df = BondFirstFilter(endDate, apikey)
    chunzhai = stockfund4df[0]
    zhuanzhai = stockfund4df[1]
    print("第一次筛选运行时间：", time.perf_counter() - start, "秒")

    print("——————————————————————————————————获取基金公司标签——————————————————————————————")
    company4df = Getbondfund4Long(lastYearDate, lastQuarDate, apikey, 1)
    print("获取基金公司标签运行时间：", time.perf_counter() - start, "秒")

    print("——————————————————————————————————获取久期标签——————————————————————————————")
    time4df = Getbondfund4Long(lastYearDate, lastQuarDate, apikey, 2)
    print("获取久期标签运行时间：", time.perf_counter() - start, "秒")

    print("——————————————————————————————————获取杠杆比例标签——————————————————————————————")
    lever4df = Getbondfund4Long(lastYearDate, lastQuarDate, apikey, 3)
    print("获取杠杆比例标签运行时间：", time.perf_counter() - start, "秒")

    print("——————————————————————————————————获取债券种类标签——————————————————————————————")
    bondtype4df = Getbondfund4Long(lastYearDate, lastQuarDate, apikey, 4)
    print("获取债券种类标签运行时间：", time.perf_counter() - start, "秒")

    print("——————————————————————————————————获取定开标签——————————————————————————————")
    dingkai4df = getdingkai()
    print("获取定开标签运行时间：", time.perf_counter() - start, "秒")

    chunzhai = pd.merge(chunzhai[['thscode', 'ths_fund_short_name_fund', 'ths_fund_manager_current_fund',
                                  'ths_invest_type_second_classi_fund']], company4df, on='thscode', how='left')
    chunzhai = pd.merge(chunzhai, time4df, on='thscode', how='left')
    chunzhai = pd.merge(chunzhai, lever4df, on='thscode', how='left')
    chunzhai = pd.merge(chunzhai, bondtype4df, on='thscode', how='left')
    chunzhai = pd.merge(chunzhai, dingkai4df, on='thscode', how='left')
    chunzhai.to_csv('output/ChunzhaiFund/chunzhai_label.csv')

    for item in ['bigcompany', 'Duration', 'lever', 'bondtype','是否为定开']:
        types = chunzhai[item].dropna().unique().tolist()
        for i in range(len(types)):
            fund0 = chunzhai[chunzhai[item] == types[i]]
            print("{}基金的个数为：{}".format(types[i], len(fund0)))
