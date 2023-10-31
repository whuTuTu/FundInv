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

from InvokingFunction.GetQuantitativeIndex import calculate_one_cum_return, calculate_max_drawdown, \
    calculate_sharpe_ratio


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
        print(onenetvalue4list)

        # 年初至今
        cumreturnY4list.append(calculate_one_cum_return(onenetvalue4list))
        maxdrawdownY4list.append(calculate_max_drawdown(onenetvalue4list))
        shaperatioY4list.append(calculate_sharpe_ratio(onenetvalue4list))

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

