# -*- coding: UTF-8 -*-
"""
@Project ：FundInv
@File    ：Evaluate.py
@IDE     ：PyCharm
@Author  ：tutu
@Date    ：2023-09-15 14:55
通过计算定量的指标用于基金评价
"""
# 载入包
import pandas as pd
from iFinDPy import *  # 同花顺API接口
import getfunction

# --------------------------------------------全局变量--------------------------------------------------------
endDate = "20230922"
lastYearDate = "20230630"  # 年报/半年报报告期
lastQuarDate = "20230630"  # 季报报告期
# apikey = ["tfzqsx229", "199d5c"]
# apikey = ["tfzq1556", "752862"]
apikey = ["tfzq1928", "232596"]
thsLogin = THS_iFinDLogin(apikey[0], apikey[1])
# ------------------------------------------生成相关时间变量--------------------------------------------------------
beginDate = "20180101"  # 开始时间
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
# 读取数据
chunzhai = pd.read_csv("output/chunzhai_label.csv")
chunzhai.drop('Unnamed: 0', axis=1, inplace=True)
fundcode4list = chunzhai.iloc[:, [0]].values.tolist()
fundcode4list = [item for sublist in fundcode4list for item in sublist]
fundchar = ','.join(fundcode4list)

len_time = len(YearDate) - 1
for i in range(len_time):
    # 半年半年的获取数据
    try:
        NetValue = pd.read_csv("input/BondFundNetValue" + YearDate[i] + '-' + YearDate[i + 1] + ".csv")
        NetValue.set_index('time', inplace=True)
    except FileNotFoundError:
        # 一段一段获取数据
        print("本地文件不存在，尝试从接口获取数据...")
        date1 = getfunction.exchangedate1(YearDate[i])
        date2 = getfunction.exchangedate1(YearDate[i + 1])

        frequency = 500
        n = int(len(fundcode4list) / frequency)
        # 末期截面基础数据
        NetValue_long = THS_HQ(','.join(fundcode4list[n * frequency::]),'accumulatedNAV','CPS:3',date1,date2).data
        for j in range(n):
            df1 = THS_HQ(','.join(fundcode4list[j * frequency:(j + 1) * frequency]),'accumulatedNAV','CPS:3',date1,date2).data
            NetValue_long = pd.concat([NetValue_long, df1])

        NetValue = NetValue_long.pivot(index='time', columns='thscode', values='accumulatedNAV')
        NetValue.to_csv("input/BondFundNetValue" + YearDate[i] + '-' + YearDate[i + 1] + ".csv")
        NetValue = pd.read_csv("input/BondFundNetValue" + YearDate[i] + '-' + YearDate[i + 1] + ".csv")
        NetValue.set_index('time', inplace=True)

    if i == 0:
        # 纵向拼接
        NetValueDF = NetValue
    else:
        NetValueDF = pd.concat([NetValueDF, NetValue])

print(NetValueDF.head())
print(NetValueDF.shape)

for i in range(len_time):
    # 纯债基金指数
    try:
        index4df = pd.read_csv("input/chunzhai_index" + YearDate[i] + '-' + YearDate[i + 1] + ".csv")
        index4df.set_index('time', inplace=True)
    except FileNotFoundError:
        # 一段一段获取数据
        print("本地文件不存在，尝试从接口获取数据...")
        date1 = getfunction.exchangedate1(YearDate[i])
        date2 = getfunction.exchangedate1(YearDate[i + 1])
        index4df = THS_HQ('930609.CSI', 'close', 'CPS:3', date1, date2).data
        index4df.to_csv("input/chunzhai_index" + YearDate[i] + '-' + YearDate[i + 1] + ".csv")
        index4df = pd.read_csv("input/chunzhai_index" + YearDate[i] + '-' + YearDate[i + 1] + ".csv")
        index4df.set_index('time', inplace=True)

    if i == 0:
        # 纵向拼接
        chunzhai_index4df = index4df
    else:
        chunzhai_index4df = pd.concat([chunzhai_index4df, index4df])

print(chunzhai_index4df.head())
print(chunzhai_index4df.shape)

# 数据缺失值如何处理??????????????????????????????????????????????????????
partfundcode4list = NetValueDF.columns

# 近三年指标
start_date = str(int(endDate[0:4])-1)+endDate[4::]
end_date = endDate
cumreturn3Y4list = []
for onecode in partfundcode4list:
    onenetvalue4list = NetValueDF.loc[getfunction.exchangedate1(start_date):getfunction.exchangedate1(end_date), onecode].values.tolist()
    chunzhai_index4list = chunzhai_index4df.loc[getfunction.exchangedate1(start_date):getfunction.exchangedate1(end_date),'close'].values.tolist()
    cumreturn3Y4list.append(getfunction.calculate_one_cum_return(onenetvalue4list))
    
print(cumreturn3Y4list) #


