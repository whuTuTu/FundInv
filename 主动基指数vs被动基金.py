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
import plotly.graph_objects as go
import plotly.offline as py_offline
config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")
# --------------------------------------------全局变量--------------------------------------------------------
beginDate = config.get("time", "beginDate")
endDate = config.get("time", "endDate")
lastYearDate = config.get("time", "lastYearDate")
lastQuarDate = config.get("time", "lastQuarDate")
apikey = [config.get("apikey", "ID1"), config.get("apikey", "password1")]
thsLogin = THS_iFinDLogin(apikey[0], apikey[1])
# ------------------------------------------生成相关时间变量---------------------------------------------------
QuanDate = getQtime4liet(beginDate, lastQuarDate)
HYearDate = getHYtime4list(beginDate, lastYearDate)
# ------------------------------------------以下为代码--------------------------------------------------------
cumrate4list = []
partHYDate = HYearDate[2::]
len_date = len(partHYDate)-1
for i in range(len_date):
    print("-------------" + partHYDate[i] + "-----------------")
    # 半年度获取数据
    indindex4df = getindex(flag=1,yesend=False,beginDate=partHYDate[i],lastYearDate=partHYDate[i+1])
    ind4df = GetindindexData(beginDate=partHYDate[i], endDate=partHYDate[i+1], apikey = apikey)
    nummin = min(len(ind4df),len(indindex4df))

    list1 = []
    for j in range(6):
        list1.append(calculate_excess_one_cum_return(indindex4df.iloc[-nummin::, j].tolist(), ind4df.iloc[-nummin::, j].tolist()))
    cumrate4list.append(list1)
print(cumrate4list)
cumrate4listnew = [[cumrate4list[i][j]*100 for i in range(len(cumrate4list))] for j in range(len(cumrate4list[0]))]
print(cumrate4listnew)
colnames = indindex4df.columns
print(colnames)
fig = go.Figure(data=[
        go.Bar(name=colnames[0], x=partHYDate[0:9], y=cumrate4listnew[0], text=cumrate4listnew[0],textposition="auto"),
        go.Bar(name=colnames[1], x=partHYDate[0:9], y=cumrate4listnew[1], text=cumrate4listnew[1],textposition="auto"),
        go.Bar(name=colnames[2], x=partHYDate[0:9], y=cumrate4listnew[2], text=cumrate4listnew[2],textposition="auto"),
        go.Bar(name=colnames[3], x=partHYDate[0:9], y=cumrate4listnew[3], text=cumrate4listnew[3],textposition="auto"),
        go.Bar(name=colnames[4], x=partHYDate[0:9], y=cumrate4listnew[4], text=cumrate4listnew[4],textposition="auto"),
        go.Bar(name=colnames[5], x=partHYDate[0:9], y=cumrate4listnew[5], text=cumrate4listnew[5],textposition="auto")
    ])
fig.update_layout(barmode='group')
fig.update_layout(title_text='行业超额检测')
fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
py_offline.plot(fig, filename='output/StockFund/行业超额检测.html')
