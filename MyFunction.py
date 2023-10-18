# -*- coding: UTF-8 -*-
"""
@Project ：FundInv 
@File    ：MyFunction.py
@IDE     ：PyCharm 
@Author  ：tutu
@Date    ：2023-08-15 11:20
该文件用于储存各类自定义函数，方便调用
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
