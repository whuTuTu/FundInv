# -*- coding: UTF-8 -*-
"""
@Project :FundInv
@File    :主动基指数vs被动基金.py
@IDE     :Pycharm
@Author  :tutu
@Date    :2023/11/11 19:15
"""
from InvokingFunction.GetData import GetindindexData
from InvokingFunction.GetGFunction import getQtime4liet, getHYtime4list, exchangedate1
from InvokingFunction.GetQuantitativeIndex import calculate_excess_one_cum_return
from InvokingFunction.Getindex import getindex
from iFinDPy import *  # 同花顺API接口
import configparser
config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")
# --------------------------------------------全局变量--------------------------------------------------------
beginDate = config.get("time", "beginDate")
endDate = config.get("time", "endDate")
lastYearDate = config.get("time", "lastYearDate")
lastQuarDate = config.get("time", "lastQuarDate")
apikey = [config.get("apikey", "ID1"),config.get("apikey", "password1")]
thsLogin = THS_iFinDLogin(apikey[0], apikey[1])
# ------------------------------------------生成相关时间变量---------------------------------------------------
QuanDate = getQtime4liet(beginDate, lastQuarDate)
print(QuanDate)
HYearDate = getHYtime4list(beginDate, lastYearDate)
print(HYearDate)
# ------------------------------------------以下为代码--------------------------------------------------------
indindex4df = getindex(flag=1)
print(indindex4df.head())
ind4df = GetindindexData(beginDate,endDate,apikey)
print(ind4df.head())
num = min(len(ind4df), len(indindex4df))
cumrate4list = []
cumrateY4list = []
partHYDate = HYearDate[2::]
print(partHYDate)
for i in range(6):
    cumrate4list.append(calculate_excess_one_cum_return(indindex4df.iloc[-num::,i].tolist(),ind4df.iloc[-num::,i].tolist()))
    list1 = []
    for j in range(len(partHYDate)-1):
        print("-------------"+partHYDate[j]+"-----------------")
        start_date = partHYDate[j]
        end_date = partHYDate[j+1]
        onenetvalue4list = indindex4df[start_date:end_date].iloc[:, i].values.tolist()
        print(len(onenetvalue4list))
        indindexnetvalue4list = ind4df[start_date:end_date].iloc[:, i].values.tolist()
        print(len(indindexnetvalue4list))
        num_min = min(len(onenetvalue4list),len(indindexnetvalue4list))
        indindex4df[start_date:end_date].iloc[:, i].to_csv("test1.csv")
        ind4df[start_date:end_date].iloc[:, i].to_csv("test2.csv")
        cumrate3y4float = calculate_excess_one_cum_return(onenetvalue4list[:num_min], indindexnetvalue4list[:num_min])
        list1.append(cumrate3y4float)
    cumrateY4list.append(list1)
print(cumrateY4list)

