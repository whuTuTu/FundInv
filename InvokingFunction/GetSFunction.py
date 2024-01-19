# -*- coding: UTF-8 -*-
"""
@Project ：FundInv 
@File    ：GetSFunction.py
@IDE     ：PyCharm 
@Author  ：tutu
@Date    ：2023-08-15 11:20
该文件用于储存较为特定的函数，主要用于股票基金的函数，不怎么具有通用性
"""
# 载入包
from math import fabs  # 浮点数取绝对值
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.offline as py_offline
import matplotlib.pyplot as plt

from InvokingFunction.GetGFunction import exchangedate1, df2list
from InvokingFunction.GetQuantitativeIndex import calculate_one_cum_return, calculate_max_drawdown, \
    calculate_sharpe_ratio, calculate_win_rate, calculate_odds_ratio


# 小于临界值且最接近临界值
def find_nearest_below1(group, target_ratio, cum_col, flag_col):
    filtered_group = group[group[cum_col] <= target_ratio]
    if not filtered_group.empty:
        nearest_idx = (target_ratio - filtered_group[cum_col]).idxmin()
        return group.loc[nearest_idx, flag_col]
    else:
        return None


# 大于临界值且最接近临界值
def find_nearest_above1(group, target_ratio, cum_col, flag_col):
    filtered_group = group[group[cum_col] >= target_ratio]
    if not filtered_group.empty:
        nearest_idx = (target_ratio - filtered_group[cum_col]).idxmax()
        return group.loc[nearest_idx, flag_col]
    else:
        return None


# 最接近临界值
def find_nearest1(row, DF, target_ratio, cum_col, flag_col):
    nearest_idx = (target_ratio - DF[cum_col]).apply(fabs).idxmin()
    return DF.loc[nearest_idx, flag_col]


def getstock1industry(aStockIndDF):
    """
    根据股票的中信行业分类进行行业主题分类
    :param aStockIndDF:
    :return: df
    """
    # 一级分类
    xiaofei = ['食品饮料', '商贸零售', '消费者服务', '家电', '纺织服', '农林牧渔']
    yiyao = ['医药']
    zhouqi = ['石油石化', '煤炭', '有色金属', '钢铁', '基础化工', '建筑', '建材', '轻工制造']
    zhizhao = ['机械', '电力设备及新能源', '国防军工', '汽车']
    TMT = ['通信', '计算机', '传媒', '电子']
    JRDC = ['银行', '非银行金融', '综合金融', '房地产']
    # others = ['交通运输、电力及公用事业、综合']

    # 三级分类特例
    alist = ['航运', '航空', '港口']
    clist = ['乘用车Ⅲ', '摩托车及其他', '汽车消费及服务Ⅲ']
    dlist = ['家具', '文娱轻工', '其他家居']

    # 分类
    for index, row in aStockIndDF.iterrows():
        if row['firstInd'] in xiaofei:
            aStockIndDF.loc[index, 'IND'] = '消费'
        elif row['firstInd'] in yiyao:
            aStockIndDF.loc[index, 'IND'] = '医药'
        elif row['firstInd'] in zhouqi:
            if row['firstInd'] == '轻工制造' and row['thirdInd'] in dlist:
                aStockIndDF.loc[index, 'IND'] = '消费'
            else:
                aStockIndDF.loc[index, 'IND'] = '周期'
        elif row['firstInd'] in zhizhao:
            if row['firstInd'] == '汽车' and row['thirdInd'] in clist:
                aStockIndDF.loc[index, 'IND'] = '消费'
            else:
                aStockIndDF.loc[index, 'IND'] = '制造'
        elif row['firstInd'] in TMT:
            aStockIndDF.loc[index, 'IND'] = 'TMT'
        elif row['firstInd'] in JRDC:
            aStockIndDF.loc[index, 'IND'] = '金融地产'
        elif row['firstInd'] == '交通运输' and row['thirdInd'] in alist:
            aStockIndDF.loc[index, 'IND'] = '周期'
        else:
            aStockIndDF.loc[index, 'IND'] = '其他'

    return aStockIndDF


def indexreturn2quantitative(types, ReturnDF):
    """

    :param types:
    :param ReturnDF:
    :return:
    """
    # 计算指标
    cumreturnY4list = []  # 年初至今累计收益
    maxdrawdownY4list = []  # 年初至今最大回撤
    shaperatioY4list = []  # 年初至今夏普比例

    cumreturnM4list = []  # 滚动一个月累计收益
    maxdrawdownM4list = []  # 滚动一个月最大回撤
    shaperatioM4list = []  # 滚动一个月夏普比例

    cumreturnW4list = []  # 本周累计收益
    maxdrawdownW4list = []  # 本周最大回撤
    shaperatioW4list = []  # 本周夏普比例

    for col_name in types:
        onenetvalue4list = ReturnDF[col_name].tolist()
        print(ReturnDF)
        print(onenetvalue4list)

        # 年初至今
        cumreturnY4list.append(calculate_one_cum_return(onenetvalue4list[243::]))
        maxdrawdownY4list.append(calculate_max_drawdown(onenetvalue4list[243::]))
        shaperatioY4list.append(calculate_sharpe_ratio(onenetvalue4list[243::]))

        # 滚动一个月
        cumreturnM4list.append(calculate_one_cum_return(onenetvalue4list[-30::]))
        maxdrawdownM4list.append(calculate_max_drawdown(onenetvalue4list[-30::]))
        shaperatioM4list.append(calculate_sharpe_ratio(onenetvalue4list[-30::]))

        # 本周
        cumreturnW4list.append(calculate_one_cum_return(onenetvalue4list[-6::]))
        maxdrawdownW4list.append(calculate_max_drawdown(onenetvalue4list[-6::]))
        shaperatioW4list.append(calculate_sharpe_ratio(onenetvalue4list[-6::]))

    data = {
        '指数名称': types,
        '年初至今累计收益': cumreturnY4list,
        '年初至今最大回撤': maxdrawdownY4list,
        '年初至今夏普比例': shaperatioY4list,
        '滚动一个月累计收益': cumreturnM4list,
        '滚动一个月最大回撤': maxdrawdownM4list,
        '滚动一个月夏普比例': shaperatioM4list,
        '本周累计收益': cumreturnW4list,
        '本周最大回撤': maxdrawdownW4list,
        '本周夏普比例': shaperatioW4list,
            }
    quantitative4df = pd.DataFrame(data)
    return quantitative4df


def returndf2fig(ReturnDF):
    """
    画图
    :param ReturnDF:
    :return:
    """
    ReturnDF.reset_index(inplace=True)
    ReturnDF = ReturnDF.drop_duplicates(subset='time', keep='first')
    col_names = ReturnDF.columns
    colnum = len(col_names)
    # 绘制折线图
    plot_data = []
    for i in range(colnum - 1):
        scatter_i = go.Scatter(x=ReturnDF[col_names[0]], y=ReturnDF[col_names[i + 1]], mode='lines',
                               name=col_names[i + 1])
        plot_data.append(scatter_i)

    layout = go.Layout(title='', showlegend=True)  # 设置 showlegend 为 True
    fig = go.Figure(data=plot_data, layout=layout)
    return fig

def gettopnlist(n1,n2,partfundcode4list,NetValueDF,endDate,num_pen,choice='gg'):
    """

    :param n1:
    :param n2:
    :param partfundcode4list:
    :param NetValueDF:
    :param endDate:
    :param num_pen:
    :param choice: gg,gb
    :return:
    """

    # 近三年指标
    start_date5Y = str(int(endDate[0:4]) - n1) + endDate[4::]  # 时间往前推5年
    start_date1Y = str(int(endDate[0:4]) - n2) + endDate[4::]

    end_date = endDate
    cumreturn5Y4list = []  # 近5年累计收益
    maxdrawdown5Y4list = []  # 近5年最大回撤
    shaperatio5Y4list = []  # 近5年夏普比例
    winrate5Y4list = []  # 近5年胜率
    oddsrate5Y4list = []  # 近5年赔率

    cumreturn1Y4list = []  # 近1年累计收益
    maxdrawdown1Y4list = []  # 近1年最大回撤
    shaperatio1Y4list = []  # 近1年夏普比例
    winrate1Y4list = []  # 近1年胜率
    oddsrate1Y4list = []  # 近1年赔率

    for onecode in partfundcode4list:
        onenetvalue4list1 = NetValueDF.loc[exchangedate1(start_date5Y):exchangedate1(end_date), onecode].values.tolist()
        onenetvalue4list2 = NetValueDF.loc[exchangedate1(start_date1Y):exchangedate1(end_date), onecode].values.tolist()

        # 近5年指标
        cumreturn5Y4list.append(calculate_one_cum_return(onenetvalue4list1))
        maxdrawdown5Y4list.append(calculate_max_drawdown(onenetvalue4list1))
        shaperatio5Y4list.append(calculate_sharpe_ratio(onenetvalue4list1))
        winrate5Y4list.append(calculate_win_rate(onenetvalue4list1))
        oddsrate5Y4list.append(calculate_odds_ratio(onenetvalue4list1))

        # 近1年指标
        cumreturn1Y4list.append(calculate_one_cum_return(onenetvalue4list2))
        maxdrawdown1Y4list.append(calculate_max_drawdown(onenetvalue4list2))
        shaperatio1Y4list.append(calculate_sharpe_ratio(onenetvalue4list2))
        winrate1Y4list.append(calculate_win_rate(onenetvalue4list2))
        oddsrate1Y4list.append(calculate_odds_ratio(onenetvalue4list2))

    data = {
        '基金代码': partfundcode4list,
        '近n1年累计收益': cumreturn5Y4list,
        '近n1年最大回撤': maxdrawdown5Y4list,
        '近n1年夏普比例': shaperatio5Y4list,
        '近n1年胜率': winrate5Y4list,
        '近n1年赔率': oddsrate5Y4list,

        '近n2年累计收益': cumreturn1Y4list,
        '近n2年最大回撤': maxdrawdown1Y4list,
        '近n2年夏普比例': shaperatio1Y4list,
        '近n2年胜率': winrate1Y4list,
        '近n2年赔率': oddsrate1Y4list
        }
    quantitative4df = pd.DataFrame(data)
    # 排序求均值
    quantitative4df['近n1年累计收益排名'] = quantitative4df['近n1年累计收益'].rank(method='first')  # 升序排列，数值较小的获得较低的排名
    quantitative4df['近n1年最大回撤排名'] = quantitative4df['近n1年最大回撤'].rank(method='first')
    quantitative4df['近n1年夏普比例排名'] = quantitative4df['近n1年夏普比例'].rank(method='first')
    quantitative4df['近n1年夏普比例排名'] = quantitative4df['近n1年夏普比例'].rank(method='first')
    quantitative4df['近n1年赔率排名'] = quantitative4df['近n1年赔率'].rank(method='first')

    if choice == 'gb':
        quantitative4df['近n2年累计收益排名'] = quantitative4df['近n2年累计收益'].rank(method='first', ascending=False)
        quantitative4df['近n2年最大回撤排名'] = quantitative4df['近n2年最大回撤'].rank(method='first', ascending=False)
        quantitative4df['近n2年夏普比例排名'] = quantitative4df['近n2年夏普比例'].rank(method='first', ascending=False)
        quantitative4df['近n2年胜率排名'] = quantitative4df['近n2年胜率'].rank(method='first', ascending=False)
        quantitative4df['近n2年赔率排名'] = quantitative4df['近n2年赔率'].rank(method='first', ascending=False)
    else:
        quantitative4df['近n2年累计收益排名'] = quantitative4df['近n2年累计收益'].rank(method='first')
        quantitative4df['近n2年最大回撤排名'] = quantitative4df['近n2年最大回撤'].rank(method='first')
        quantitative4df['近n2年夏普比例排名'] = quantitative4df['近n2年夏普比例'].rank(method='first')
        quantitative4df['近n2年胜率排名'] = quantitative4df['近n2年胜率'].rank(method='first')
        quantitative4df['近n2年赔率排名'] = quantitative4df['近n2年赔率'].rank(method='first')
    quantitative4df = quantitative4df.dropna()
    quantitative4df['总排名'] = quantitative4df.iloc[:, 10:-1].mean(axis=1)
    quantitative4df = quantitative4df.sort_values(by='总排名', ascending=False)  # 降序排列
    fund4list = df2list(quantitative4df.iloc[:, [0]])[0:int(len(quantitative4df) * num_pen)]
    return fund4list

