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
from InvokingFunction.GetData import GetbfundnetvalueData, GetsfundnetvalueData
from InvokingFunction.GetGFunction import exchangedate1, getQtime4liet, getHYtime4list, getchunzhaicode, getstockfundcode
from InvokingFunction.GetQuantitativeIndex import calculate_excess_cum_returns, calculate_excess_sharpe_ratio
from InvokingFunction.Getindex import getindex
from InvokingFunction.Short2Long import Getstockfund4Long, Getbondfund4Long

config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")
# --------------------------------------------全局变量--------------------------------------------------------
beginDate = config.get("time", "beginDate")
endDate = config.get("time", "endDate")
lastYearDate = config.get("time", "lastYearDate")
lastQuarDate = config.get("time", "lastQuarDate")
apikey = [config.get("apikey", "ID1"),config.get("apikey", "password1")]
thsLogin = THS_iFinDLogin(apikey[0], apikey[1])
choice = 'chunzhai'
# ------------------------------------------生成相关时间变量---------------------------------------------------
QuanDate = getQtime4liet(beginDate, lastQuarDate)
HYearDate = getHYtime4list(beginDate, lastYearDate)
# ------------------------------------------以下为代码--------------------------------------------------------
if choice == 'stock':
    # 基金净值数据
    fundcode4list = getstockfundcode()  # 获取纯债基金代码
    print("初筛池股票基金数量：{}".format(len(fundcode4list)))
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

    # 基金行业分类数据和风格分类数据
    bondtype4df = Getstockfund4Long(lastYearDate, lastYearDate, apikey, 1)
    style4df = Getstockfund4Long(lastYearDate, lastYearDate, apikey, 3)

    # 指数的走势数据
    index4ind = getindex(flag=1)  # 行业走势

    # 数据缺失值暂时不管
    partfundcode4list = NetValueDF.columns
    partfundcode4list2 = []
    cumrate3y4list = []
    shaperatio3y4list = []
    cumratehy4list = []
    shaperatiohy4list = []
    for onecode in partfundcode4list:
        # 排除不存在标签的基金
        if onecode in bondtype4df['thscode'].values:
            ind4char = bondtype4df.loc[bondtype4df['thscode'] == onecode, '行业标签'].iloc[0]
        else:
            print(f"The value {onecode} does not exist in 'thscode' column.")
            continue

        if ind4char == '行业轮动基金':
            continue
        else:
            ind4char = ind4char[2::]

        partfundcode4list2.append(onecode)

        # 长期指标：滚动三年的数据
        list1 = []
        list2 = []
        for onetime in QuanDate[-8::]:
            n1 = 3  # 滚动三年
            start_date3Y = str(int(onetime[0:4]) - n1) + onetime[4::]
            end_date = onetime
            onenetvalue4list = NetValueDF.loc[exchangedate1(start_date3Y):exchangedate1(end_date), onecode].values.tolist()
            indindexnetvalue4list = index4ind.loc[exchangedate1(start_date3Y):exchangedate1(end_date), ind4char].values.tolist()
            cumrate3y4float = calculate_excess_cum_returns(onenetvalue4list, indindexnetvalue4list)
            sharatio4float = calculate_excess_sharpe_ratio(onenetvalue4list, indindexnetvalue4list)
            list1.append(cumrate3y4float[-1])  # 一个基金8期的滚动累计收益率
            list2.append(sharatio4float)

        cumrate3y4list.append(sum(list1)/len(list1))
        shaperatio3y4list.append(sum(list2)/len(list2))

        # 短期数据：近半年指标
        onenetvalue4list = NetValueDF.tail(180)[onecode].tolist()
        indindexnetvalue4list = index4ind.tail(180)[ind4char].tolist()
        cumratehy4list.append(calculate_excess_cum_returns(onenetvalue4list, indindexnetvalue4list)[-1])
        shaperatiohy4list.append(calculate_excess_sharpe_ratio(onenetvalue4list, indindexnetvalue4list))

    quantitative4df = pd.DataFrame({
        'thscode': partfundcode4list2,
        '3年滚动累计超额收益率均值': cumrate3y4list,
        '3年滚动超额夏普比例': shaperatio3y4list,
        '近130个交易日累计超额收益率': cumratehy4list,
        '近130个交易日超额夏普比例': shaperatiohy4list
    })

    quantitative4df['3年滚动累计超额收益率均值排名'] = quantitative4df['3年滚动累计超额收益率均值'].rank(method='first')  # 升序排列，数值较小的获得较低的排名
    quantitative4df['3年滚动超额夏普比例排名'] = quantitative4df['3年滚动超额夏普比例'].rank(method='first')
    quantitative4df['近130个交易日累计超额收益率排名'] = quantitative4df['近130个交易日累计超额收益率'].rank(method='first')
    quantitative4df['近130个交易日超额夏普比例排名'] = quantitative4df['近130个交易日超额夏普比例'].rank(method='first')
    quantitative4df['总得分'] = quantitative4df.iloc[:, -4::].mean(axis=1)
    quantitative4df = quantitative4df.sort_values(by='总得分', ascending=False)  # 降序排列

    # 读取基金基本信息数据
    basicdata4df = pd.read_csv("output/StockFund/stockfund_label.csv")
    quantitative4df = pd.merge(basicdata4df,quantitative4df,on='thscode',how='right')
    quantitative4df.to_csv("output/StockFund/股票基金以行业指数为基准打分.csv")

if choice == 'chunzhai':
    # 基金净值数据
    fundcode4list = getchunzhaicode()  # 获取纯债基金代码
    print("初筛池股票基金数量：{}".format(len(fundcode4list)))
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

    # 基金债券种类
    bondtype4df = Getbondfund4Long(lastYearDate, lastQuarDate, apikey, flag=4)

    # 指数的走势数据
    index4ind = getindex(flag=3)  # 行业走势

    # 数据缺失值暂时不管
    partfundcode4list = NetValueDF.columns
    partfundcode4list2 = []
    cumrate3y4list = []
    shaperatio3y4list = []
    cumratehy4list = []
    shaperatiohy4list = []
    for onecode in partfundcode4list:
        # 排除不存在标签的基金
        if onecode in bondtype4df['thscode'].values:
            ind4char = bondtype4df.loc[bondtype4df['thscode'] == onecode, 'bondtype'].iloc[0]
        else:
            print(f"The value {onecode} does not exist in 'thscode' column.")
            continue

        partfundcode4list2.append(onecode)

        # 长期指标：滚动三年的数据
        list1 = []
        list2 = []
        for onetime in QuanDate[-8::]:
            n1 = 3  # 滚动三年
            start_date3Y = str(int(onetime[0:4]) - n1) + onetime[4::]
            end_date = onetime
            onenetvalue4list = NetValueDF.loc[exchangedate1(start_date3Y):exchangedate1(end_date),onecode].values.tolist()
            indindexnetvalue4list = index4ind.loc[exchangedate1(start_date3Y):exchangedate1(end_date),ind4char].values.tolist()
            cumrate3y4float = calculate_excess_cum_returns(onenetvalue4list, indindexnetvalue4list)
            sharatio4float = calculate_excess_sharpe_ratio(onenetvalue4list, indindexnetvalue4list)
            list1.append(cumrate3y4float[-1])  # 一个基金8期的滚动累计收益率
            list2.append(sharatio4float)

        cumrate3y4list.append(sum(list1) / len(list1))
        shaperatio3y4list.append(sum(list2) / len(list2))

        # 短期数据：近半年指标
        onenetvalue4list = NetValueDF.tail(180)[onecode].tolist()
        indindexnetvalue4list = index4ind.tail(180)[ind4char].tolist()
        cumratehy4list.append(calculate_excess_cum_returns(onenetvalue4list, indindexnetvalue4list)[-1])
        shaperatiohy4list.append(calculate_excess_sharpe_ratio(onenetvalue4list, indindexnetvalue4list))

    quantitative4df = pd.DataFrame({
        'thscode': partfundcode4list2,
        '3年滚动累计超额收益率均值': cumrate3y4list,
        '3年滚动超额夏普比例': shaperatio3y4list,
        '近130个交易日累计超额收益率': cumratehy4list,
        '近130个交易日超额夏普比例': shaperatiohy4list
    })

    quantitative4df['3年滚动累计超额收益率均值排名'] = quantitative4df['3年滚动累计超额收益率均值'].rank(method='first')  # 升序排列，数值较小的获得较低的排名
    quantitative4df['3年滚动超额夏普比例排名'] = quantitative4df['3年滚动超额夏普比例'].rank(method='first')
    quantitative4df['近130个交易日累计超额收益率排名'] = quantitative4df['近130个交易日累计超额收益率'].rank(method='first')
    quantitative4df['近130个交易日超额夏普比例排名'] = quantitative4df['近130个交易日超额夏普比例'].rank(method='first')
    quantitative4df['总得分'] = quantitative4df.iloc[:, -4::].mean(axis=1)
    quantitative4df = quantitative4df.sort_values(by='总得分', ascending=False)  # 降序排列

    # 读取基金基本信息数据
    basicdata4df = pd.read_csv("output/ChunzhaiFund/chunzhai_label.csv")
    quantitative4df = pd.merge(basicdata4df, quantitative4df, on='thscode', how='right')
    quantitative4df.to_csv("output/StockFund/债券基金以债券种类指数为基准打分.csv")
