# -*- coding: UTF-8 -*-
"""
@Project ：FundInv
@File    ：index.py
@IDE     ：PyCharm
@Author  ：tutu
@Date    ：2023-08-24 10:29
标签均为长期标签，构建基金指数序列为短期标签
"""
# 载入包
import pandas as pd
from iFinDPy import *  # 同花顺API接口
import time
import plotly.graph_objects as go
import plotly.offline as py_offline
import matplotlib.pyplot as plt

from StyleShort import StyleShort
from firstfilter import FirstFilter
from InvokingFunction.Short2Long import Getstockfund4Long
from IndependentFund import getIndependent
import warnings
warnings.filterwarnings(action='ignore')
warnings.filterwarnings(action='ignore')  # 导入warnings模块，并指定忽略代码运行中的警告信息
plt.rcParams['font.sans-serif'] = ['SimHei']  # 解决中文显示乱码的问题
plt.rcParams['axes.unicode_minus'] = False

start = time.perf_counter()  # 代码开始的时间

# --------------------------------------------全局变量--------------------------------------------------------

endDate = "20230922"
lastYearDate = "20230630"  # 年报/半年报报告期
lastQuarDate = "20230630"  # 季报报告期
# apikey = ["tfzqsx229", "199d5c"]
apikey = ["tfzq1556", "752862"]
thsLogin = THS_iFinDLogin("tfzq1556", "752862")
Hflag = False
ind_flag = False
style_flag = True

# ------------------------------------------生成相关时间变量--------------------------------------------------------
beginDate = "20210630"  # 开始时间
endDate1 = endDate[0:4] + '-' + endDate[4:6] + '-' + endDate[6::]
beginyear = beginDate[0:4]
endyear = endDate[0:4]
monthday = ['0331', '0630', '0930', '1231']
aRepDate = [str(i) + j for i in range(int(beginyear), int(endyear) + 1) for j in monthday]
QuanDate = []
for j in aRepDate:
    if lastQuarDate >= j >= beginDate:
        QuanDate.append(j)
    else:
        continue
QuanDate.append(endDate)

monthday = ['0630', '1231']
aRepDate = [str(i) + j for i in range(int(beginyear), int(endyear) + 1) for j in monthday]
YearDate = []
for j in aRepDate:
    if lastYearDate >= j >= beginDate:
        YearDate.append(j)
    else:
        continue
YearDate.append(endDate)

print(YearDate)
print(len(YearDate))

# ------------------------------------------以下为代码--------------------------------------------------------
# 共振因子
if Hflag:
    myfund = FirstFilter(endDate, apikey)
    len_time = len(QuanDate) - 1
    for i in range(len_time):
        print("---------------------{}------------------------".format(QuanDate[i]))
        HDF = getIndependent(QuanDate[i], apikey)
        print("已获取{}的共振因子标签数据".format(QuanDate[i]))

        # 合并数据
        MyFundDF = pd.merge(myfund, HDF, on='thscode', how='left')

        # 读取数据
        fund = MyFundDF.iloc[:, [0]].values.tolist()
        fund = [item for sublist in fund for item in sublist]
        fundchar = ','.join(fund)
        try:
            NetValue = pd.read_csv("input/NetValue" + QuanDate[i] + ".csv")
            NetValue.set_index('time', inplace=True)
        except FileNotFoundError:
            # 一段一段获取数据
            print("本地文件不存在，尝试从接口获取数据...")
            date1 = QuanDate[i][0:4] + '-' + QuanDate[i][4:6] + '-' + QuanDate[i][6::]
            date2 = QuanDate[i + 1][0:4] + '-' + QuanDate[i + 1][4:6] + '-' + QuanDate[i + 1][6::]
            NetValue_long = THS_HQ(fundchar, 'accumulatedNAV', 'CPS:3', date1, date2).data
            NetValue = NetValue_long.pivot(index='time', columns='thscode', values='accumulatedNAV')
            NetValue.to_csv("input/NetValue" + QuanDate[i] + ".csv")
            NetValue = pd.read_csv("input/NetValue" + QuanDate[i] + ".csv")
            NetValue.set_index('time', inplace=True)

        # 分类基金
        types = MyFundDF['HCategory'].dropna().unique().tolist()
        for j in range(len(types)):
            fund0 = MyFundDF[MyFundDF['HCategory'] == types[j]].iloc[:, [0]].values.tolist()
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
    ReturnDF.reset_index(inplace=True)
    col_names = ReturnDF.columns
    print(col_names)
    print(ReturnDF.head())
    # 绘制折线图
    scatter_1 = go.Scatter(x=ReturnDF[col_names[0]], y=ReturnDF[col_names[1]], mode='lines', name=col_names[1])
    scatter_2 = go.Scatter(x=ReturnDF[col_names[0]], y=ReturnDF[col_names[2]], mode='lines', name=col_names[2])
    scatter_3 = go.Scatter(x=ReturnDF[col_names[0]], y=ReturnDF[col_names[3]], mode='lines', name=col_names[3])
    plot_data = [scatter_1, scatter_2, scatter_3]
    layout = go.Layout(title='共振因子', showlegend=True)  # 设置 showlegend 为 True
    fig = go.Figure(data=plot_data, layout=layout)
    py_offline.plot(fig, filename='output/H.html')

# 行业
if ind_flag:
    myfund = FirstFilter(endDate, apikey)
    len_time = len(YearDate) - 1
    for i in range(len_time):
        print("---------------------{}------------------------".format(YearDate[i]))
        StyleShort = Getstockfund4Long(YearDate[i], apikey)
        print("已获取{}的行业风格因子标签数据".format(YearDate[i]))

        # 合并数据
        MyFundDF = pd.merge(myfund, StyleShort, on='thscode', how='left')

        # 读取数据
        fund = MyFundDF.iloc[:, [0]].values.tolist()
        fund = [item for sublist in fund for item in sublist]
        fundchar = ','.join(fund)
        try:
            NetValue = pd.read_csv("input/NetValue" + YearDate[i]+'-'+YearDate[i+1] + ".csv")
            NetValue.set_index('time', inplace=True)
        except FileNotFoundError:
            # 一段一段获取数据
            print("本地文件不存在，尝试从接口获取数据...")
            date1 = YearDate[i][0:4] + '-' + YearDate[i][4:6] + '-' + YearDate[i][6::]
            date2 = YearDate[i + 1][0:4] + '-' + YearDate[i + 1][4:6] + '-' + YearDate[i + 1][6::]
            NetValue_long = THS_HQ(fundchar, 'accumulatedNAV', 'CPS:3', date1, date2).data
            NetValue = NetValue_long.pivot(index='time', columns='thscode', values='accumulatedNAV')
            NetValue.to_csv("input/NetValue" + YearDate[i]+'-'+YearDate[i+1] +  ".csv")
            NetValue = pd.read_csv("input/NetValue" + YearDate[i]+'-'+YearDate[i+1] + ".csv")
            NetValue.set_index('time', inplace=True)

        # 分类基金
        types = MyFundDF['Stable_Count'].dropna().unique().tolist()
        for j in range(len(types)):
            fund0 = MyFundDF[MyFundDF['Stable_Count'] == types[j]].iloc[:, [0]].values.tolist()
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
    ReturnDF.reset_index(inplace=True)
    col_names = ReturnDF.columns
    colnum = len(col_names)
    print(col_names)
    print(ReturnDF.head())
    # 绘制折线图
    plot_data = []
    for i in range(colnum-1):
        scatter_i = go.Scatter(x=ReturnDF[col_names[0]], y=ReturnDF[col_names[i+1]], mode='lines', name=col_names[i+1])
        plot_data.append(scatter_i)

    layout = go.Layout(title='行业主题', showlegend=True)  # 设置 showlegend 为 True
    fig = go.Figure(data=plot_data, layout=layout)
    py_offline.plot(fig, filename='output/ind.html')

if style_flag:
    myfund = FirstFilter(endDate, apikey)
    len_time = len(YearDate) - 1
    for i in range(len_time):
        print("------------------------{0}------------------------".format(YearDate[i]))
        styleshortdf = StyleShort(YearDate[i], apikey)
        # print("已获取{}的风格因子标签数据".format(YearDate[i]))

        # 合并数据
        MyFundDF = pd.merge(myfund, styleshortdf, on='thscode', how='left')
        MyFundDF = pd.merge(MyFundDF, Getstockfund4Long(YearDate[i], apikey, 1), on='thscode', how='left')

        # 读取数据
        fund = MyFundDF.iloc[:, [0]].values.tolist()
        fund = [item for sublist in fund for item in sublist]
        fundchar = ','.join(fund)
        try:
            NetValue = pd.read_csv("input/NetValue" + YearDate[i] + '-' + YearDate[i + 1] + ".csv")
            NetValue.set_index('time', inplace=True)
        except FileNotFoundError:
            # 一段一段获取数据
            print("本地文件不存在，尝试从接口获取数据...")
            date1 = YearDate[i][0:4] + '-' + YearDate[i][4:6] + '-' + YearDate[i][6::]
            date2 = YearDate[i + 1][0:4] + '-' + YearDate[i + 1][4:6] + '-' + YearDate[i + 1][6::]
            NetValue_long = THS_HQ(fundchar, 'accumulatedNAV', 'CPS:3', date1, date2).data
            NetValue = NetValue_long.pivot(index='time', columns='thscode', values='accumulatedNAV')
            NetValue.to_csv("input/NetValue" + YearDate[i] + '-' + YearDate[i + 1] + ".csv")
            NetValue = pd.read_csv("input/NetValue" + YearDate[i] + '-' + YearDate[i + 1] + ".csv")
            NetValue.set_index('time', inplace=True)

        # 分类基金
        MyFundDF = MyFundDF[MyFundDF['Stable_Count'] == '稳定行业均衡基金']
        # types = MyFundDF['Xstyle'].dropna().unique().tolist()
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
    ReturnDF = ReturnDF.drop_duplicates(subset='time', keep='first')
    ReturnDF.reset_index(inplace=True)
    col_names = ReturnDF.columns
    colnum = len(col_names)
    print(col_names)
    print(ReturnDF.head())
    ReturnDF.to_csv("output/test.csv")
    # 绘制折线图
    plot_data = []
    for i in range(colnum - 1):
        scatter_i = go.Scatter(x=ReturnDF[col_names[0]], y=ReturnDF[col_names[i + 1]], mode='lines',
                               name=col_names[i + 1])
        plot_data.append(scatter_i)

    layout = go.Layout(title='', showlegend=True)  # 设置 showlegend 为 True
    fig = go.Figure(data=plot_data, layout=layout)
    py_offline.plot(fig, filename='output/style.html')


