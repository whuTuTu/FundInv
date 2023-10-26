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
