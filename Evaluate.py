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
from InvokingFunction.GetData import GetbfundnetvalueData, GetindexcloseData
from InvokingFunction.GetGFunction import exchangedate1, getQtime4liet, getHYtime4list, getchunzhaicode
from InvokingFunction.GetQuantitativeIndex import calculate_one_cum_return, \
    calculate_excess_sharpe_ratio, calculate_excess_max_drawdown, calculate_excess_win_rate, \
    calculate_excess_one_cum_return, calculate_max_drawdown, calculate_win_rate, calculate_excess_odds_ratio, \
    calculate_odds_ratio

# --------------------------------------------全局变量--------------------------------------------------------
endDate = "20230922"
lastYearDate = "20230630"  # 年报/半年报报告期
lastQuarDate = "20230630"  # 季报报告期
# apikey = ["tfzqsx229", "199d5c"]
# apikey = ["tfzq1556", "752862"]
apikey = ["tfzq1928", "232596"]
thsLogin = THS_iFinDLogin(apikey[0], apikey[1])
# ------------------------------------------生成相关时间变量---------------------------------------------------
beginDate = "20180101"  # 开始时间
endDate1 = exchangedate1(endDate)
QuanDate = getQtime4liet(beginDate, lastQuarDate)
YearDate = getHYtime4list(beginDate, lastYearDate)
# ------------------------------------------以下为代码--------------------------------------------------------
# 读取数据
fundcode4list = getchunzhaicode()  # 获取纯债基金代码
print(len(fundcode4list))
fundchar = ','.join(fundcode4list)

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

for i in range(len_time): # 获取纯债基金收盘价
    index4df = GetindexcloseData('930609.CSI', YearDate[i], YearDate[i + 1], apikey)  # 纯债基金指数
    if i == 0:
        # 纵向拼接
        chunzhai_index4df = index4df
    else:
        chunzhai_index4df = pd.concat([chunzhai_index4df, index4df])
chunzhai_index4df = chunzhai_index4df.drop_duplicates(subset=['time','thscode'], keep='first')
chunzhai_index4df.set_index('time', inplace=True)

print(NetValueDF.head())
print(NetValueDF.shape)
print(chunzhai_index4df.head())
print(chunzhai_index4df.shape)  # ?有10只基金没有数据

# 数据缺失值暂时不管
partfundcode4list = NetValueDF.columns

# 近三年指标
start_date = str(int(endDate[0:4])-1)+endDate[4::] # 时间往前推三年
end_date = endDate
cumreturn3Y4list = []  # 近三年累计收益
maxdrawdown3Y4list = [] # 近三年最大回撤
winrate3Y4list = [] # 近三年胜率
oddsrate3Y4list = [] # 近三年赔率

excesscumreturn3Y4list = []  # 近三年超额累计收益
excesssharpe3Y4list = []  # 近三年超额夏普比例
excessmaxdrawdown3Y4list = []  # 近三年超额最大回撤
excesswinrate3Y4list = []  # 近三年超额胜率
excessoddsrate3Y4list = []  # 近三年超额赔率

for onecode in partfundcode4list:
    onenetvalue4list = NetValueDF.loc[exchangedate1(start_date):exchangedate1(end_date), onecode].values.tolist()
    chunzhai_index4list = chunzhai_index4df.loc[exchangedate1(start_date):exchangedate1(end_date),'close'].values.tolist()

    # 普通指标
    cumreturn3Y4list.append(calculate_one_cum_return(onenetvalue4list))
    maxdrawdown3Y4list.append(calculate_max_drawdown(onenetvalue4list))
    winrate3Y4list.append(calculate_win_rate(onenetvalue4list))
    oddsrate3Y4list.append(calculate_odds_ratio(onenetvalue4list))

    # 超额指标
    excesscumreturn3Y4list.append(calculate_excess_one_cum_return(onenetvalue4list, chunzhai_index4list))
    excesssharpe3Y4list.append(calculate_excess_sharpe_ratio(onenetvalue4list, chunzhai_index4list))
    excessmaxdrawdown3Y4list.append(calculate_excess_max_drawdown(onenetvalue4list, chunzhai_index4list))
    excesswinrate3Y4list.append(calculate_excess_win_rate(onenetvalue4list, chunzhai_index4list))
    excessoddsrate3Y4list.append(calculate_excess_odds_ratio(onenetvalue4list, chunzhai_index4list))

data = {
    'thscode': partfundcode4list,
    '近三年累计收益': cumreturn3Y4list,
    '近三年最大回撤': maxdrawdown3Y4list,
    '近三年胜率': winrate3Y4list,
    '近三年赔率': oddsrate3Y4list,
    '近三年超额累计收益': excesscumreturn3Y4list,
    '近三年超额夏普比例': excesssharpe3Y4list,
    '近三年超额最大回撤': excessmaxdrawdown3Y4list,
    '近三年超额胜率': excesswinrate3Y4list,
    '近三年超额赔率': excessoddsrate3Y4list,
    }
quantitative4df = pd.DataFrame(data)
# 排序求均值
quantitative4df['近三年累计收益排名'] = quantitative4df['近三年累计收益'].rank(method='first')  # 升序排列，数值较小的获得较低的排名
quantitative4df['近三年最大回撤排名'] = quantitative4df['近三年最大回撤'].rank(method='first')
quantitative4df['近三年胜率排名'] = quantitative4df['近三年胜率'].rank(method='first')
quantitative4df['近三年赔率排名'] = quantitative4df['近三年赔率'].rank(method='first')
quantitative4df['近三年超额累计收益排名'] = quantitative4df['近三年超额累计收益'].rank(method='first')
quantitative4df['近三年超额夏普比例排名'] = quantitative4df['近三年超额夏普比例'].rank(method='first')
quantitative4df['近三年超额最大回撤排名'] = quantitative4df['近三年超额最大回撤'].rank(method='first')
quantitative4df['近三年超额胜率排名'] = quantitative4df['近三年超额胜率'].rank(method='first')
quantitative4df['近三年超额赔率排名'] = quantitative4df['近三年超额赔率'].rank(method='first')
quantitative4df = quantitative4df.dropna()
quantitative4df['总排名'] = quantitative4df.iloc[:, 9:-1].mean(axis=1)

chunzhailable4df = pd.read_csv("output/ChunzhaiFund/chunzhai_label.csv")
chunzhailable4df.drop('Unnamed: 0', axis=1, inplace=True)
quantitative4df = pd.merge(quantitative4df.iloc[:, list(range(0, 9)) + [-1]], chunzhailable4df, on='thscode', how='left')
quantitative4df = quantitative4df.sort_values(by='总排名', ascending=False)
quantitative4df.to_csv("output/ChunzhaiFund/quantitative.csv")