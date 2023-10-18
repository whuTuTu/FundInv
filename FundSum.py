# -*- coding: UTF-8 -*-
"""
@Project ：FundInv
@File    ：FundSum.py
@IDE     ：PyCharm
@Author  ：tutu
@Date    ：2023-10-10 16:38
"""
import pandas as pd
import time
import matplotlib.pyplot as plt

from bondfundfilter import BondFirstFilter
from firstfilter import FirstFilter
from short2long import getlong, bond4long
from IndependentFund import getIndependent
import warnings

warnings.filterwarnings(action='ignore')
warnings.filterwarnings(action='ignore')  # 导入warnings模块，并指定忽略代码运行中的警告信息
plt.rcParams['font.sans-serif'] = ['SimHei']  # 解决中文显示乱码的问题
plt.rcParams['axes.unicode_minus'] = False

start = time.perf_counter()  # 代码开始的时间

# 　------------------------------------------全局变量--------------------------------------------------------

endDate = "20230908"
lastYearDate = "20230630"  # 年报/半年报报告期
lastQuarDate = "20230630"  # 季报报告期
# apikey = ["tfzqsx229", "199d5c"]
apikey = ["tfzq1556", "752862"]
choice = 'bond'

# ------------------------------------------以下为代码--------------------------------------------------------
if choice == 'stock':
    print("——————————————————————————————————第一次筛选———————————————————————————————————————")
    myfund = FirstFilter(endDate, apikey)
    print("第一次筛选运行时间：", time.perf_counter() - start, "秒")

    print("——————————————————————————————————获取行业主题标签——————————————————————————————")
    Ind4df = getlong(lastYearDate, lastQuarDate, apikey, 1)
    print("获取行业主题标签运行时间：", time.perf_counter() - start, "秒")

    print("——————————————————————————————————获取大小盘标签——————————————————————————————")
    marketvalue4df = getlong(lastYearDate, lastQuarDate, apikey, 2)
    print("获取大小盘标签运行时间：", time.perf_counter() - start, "秒")

    print("——————————————————————————————————获取风格标签——————————————————————————————")
    style4df = getlong(lastYearDate, lastQuarDate, apikey, 3)
    print("获取风格标签运行时间：", time.perf_counter() - start, "秒")

    print("——————————————————————————————————获取共振因子标签———————————————————————————————————")
    h4df = getlong(lastQuarDate, lastQuarDate, apikey, 4)
    print("获取共振因子标签运行时间：", time.perf_counter() - start, "秒")

    # 合并数据
    myfund = pd.merge(myfund, Ind4df, on='thscode', how='left')
    myfund = pd.merge(myfund, marketvalue4df, on='thscode', how='left')
    myfund = pd.merge(myfund, style4df, on='thscode', how='left')
    myfund = pd.merge(myfund, h4df, on='thscode', how='left')
    myfund.to_csv("output/stockfund_label.csv")

    types = myfund['Stable_Count'].dropna().unique().tolist()
    for i in range(len(types)):
        fund0 = myfund[myfund['Stable_Count'] == types[i]].iloc[:, [0]].values.tolist()
        fund0 = [item for sublist in fund0 for item in sublist]
        print("{}基金的个数为：{}".format(types[i], len(fund0)))

    print("\n")
    types = myfund[myfund['Stable_Count'] == '稳定行业均衡基金']['XStable'].dropna().unique().tolist()
    for i in range(len(types)):
        fund0 = myfund[myfund['Stable_Count'] == '稳定行业均衡基金'][myfund['XStable'] == types[i]].iloc[:,
                [0]].values.tolist()
        fund0 = [item for sublist in fund0 for item in sublist]
        print("{}基金的个数为：{}".format(types[i], len(fund0)))

    print("\n")
    types = myfund[myfund['Stable_Count'] == '稳定行业均衡基金']['YStable'].dropna().unique().tolist()
    for i in range(len(types)):
        fund0 = myfund[myfund['Stable_Count'] == '稳定行业均衡基金'][myfund['YStable'] == types[i]].iloc[:,
                [0]].values.tolist()
        fund0 = [item for sublist in fund0 for item in sublist]
        print("{}基金的个数为：{}".format(types[i], len(fund0)))

    print("\n")
    types = myfund['independent'].dropna().unique().tolist()
    for i in range(len(types)):
        fund0 = myfund[myfund['independent'] == types[i]].iloc[:, [0]].values.tolist()
        fund0 = [item for sublist in fund0 for item in sublist]
        print("{}基金的个数为：{}".format(types[i], len(fund0)))

if choice == 'bond':
    print("——————————————————————————————————第一次筛选———————————————————————————————————————")
    myfund = BondFirstFilter(endDate, apikey)
    cunzhai = myfund[0]
    zhuanzhai = myfund[1]
    print("第一次筛选运行时间：", time.perf_counter() - start, "秒")

    print("——————————————————————————————————获取基金公司标签——————————————————————————————")
    company4df = bond4long(lastYearDate,lastQuarDate, apikey, 1)
    print("获取基金公司标签运行时间：", time.perf_counter() - start, "秒")

    print("——————————————————————————————————获取久期标签——————————————————————————————")
    time4df = bond4long(lastYearDate,lastQuarDate, apikey, 2)
    print("获取久期标签运行时间：", time.perf_counter() - start, "秒")

    print("——————————————————————————————————获取杠杆比例标签——————————————————————————————")
    lever4df = bond4long(lastYearDate,lastQuarDate, apikey, 3)
    print("获取杠杆比例标签运行时间：", time.perf_counter() - start, "秒")

    print("——————————————————————————————————获取债券种类标签——————————————————————————————")
    bondtype4df = bond4long(lastYearDate,lastQuarDate, apikey, 4)
    print("获取债券种类标签运行时间：", time.perf_counter() - start, "秒")

    cunzhai = pd.merge(cunzhai[['thscode', 'ths_fund_short_name_fund', 'ths_fund_manager_current_fund',
                                'ths_invest_type_second_classi_fund']], company4df, on='thscode', how='left')
    cunzhai = pd.merge(cunzhai, time4df, on='thscode', how='left')
    cunzhai = pd.merge(cunzhai, lever4df, on='thscode', how='left')
    cunzhai = pd.merge(cunzhai, bondtype4df, on='thscode', how='left')
    cunzhai.to_csv('output/chunzhai_label.csv')

    for item in ['bigcompany', 'Duration', 'lever', 'bondtype']:
        types = cunzhai[item].dropna().unique().tolist()
        for i in range(len(types)):
            fund0 = cunzhai[cunzhai[item] == types[i]]
            print("{}基金的个数为：{}".format(types[i], len(fund0)))
