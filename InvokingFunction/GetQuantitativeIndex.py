# -*- coding: UTF-8 -*-
"""
@Project :FundInv
@File    :GetQuantitativeIndex.py
@IDE     :Pycharm
@Author  :tutu
@Date    :2023/10/22 23:19
计算量化指标
"""
# 载入包
import numpy as np
import os
# 更改相对路径
path = "D:\TFCode\FundInv"
os.chdir(path)

# ------------------------------------------量化指标-------------------------------------------------
def netvalue2return(netvalue4list):
    """
    将基金净值转变为收益率序列
    :param netvalue4list:
    :return:初期为0
    """
    returns = [0]
    n = len(netvalue4list)
    for i in range(n):
        if i == (n-1):
            pass
        else:
            returns.append((netvalue4list[i + 1] - netvalue4list[i]) / netvalue4list[i])
    return returns

def returns2cumreturns(returns):
    """
    收益率序列转化为累计收益率序列
    :param returns:
    :return:
    """
    cumreturns = []
    cumreturn = 0
    for oneret in returns:
        cumreturn = (1+cumreturn)*(1+oneret)-1
        cumreturns.append(cumreturn)
    return cumreturns

def calculate_one_cum_return(netvalue4list):
    """
    累积收益率计算
    :param netvalue4list:list
    :return:
    """
    return (netvalue4list[-1] - netvalue4list[0]) / netvalue4list[0]

def calculate_cum_returns(netvalue4list):
    """
    累积收益率序列计算
    :param netvalue4list:list
    :return:
    """
    returns = [0]
    n = len(netvalue4list)
    cum_returns = []

    for i in range(n):
        cum_returns.append((netvalue4list[i] - netvalue4list[0]) / netvalue4list[0])
    return cum_returns


def calculate_max_drawdown(netvalue4list):
    """
    收益率最大回撤（正数）
    :param netvalue4list:list
    :return:
    """
    peak = 1
    drawdowns = []
    for onevalue in netvalue4list:
        drawdown = (onevalue - peak) / peak  # 计算回撤
        if onevalue > peak:  # 更新最高点
            peak = onevalue
        drawdowns.append(drawdown)
    max_drawdown = min(drawdowns)  # 最大回撤为回撤序列中的最小值
    return -max_drawdown

def calculate_win_rate(netvalue4list):
    """
    胜率计算
    :param netvalue4list:list
    :return:
    """
    fund_returns = netvalue2return(netvalue4list)
    num_positive_returns = sum(1 for r in fund_returns if r > 0)
    num_trading_days = len(fund_returns)
    win_rate = num_positive_returns / num_trading_days
    return win_rate


def calculate_odds_ratio(netvalue4list):
    """
    赔率(盈亏比)
    :param netvalue4list:list
    :return:
    """

    fund_returns = netvalue2return(netvalue4list)
    negative_returns = np.mean([r for r in fund_returns if r < 0])
    positive_returns = np.mean([r for r in fund_returns if r > 0])
    odds_ratio = positive_returns / negative_returns
    return odds_ratio

# ------------------------------------------超额指标-------------------------------------------------
def calculate_excess_returns(netvalue4list,standard_netvalue4list):
    """
    计算超额收益
    :param netvalue4list:
    :param standard_netvalue4list:
    :return:
    """
    fund_returns = netvalue2return(netvalue4list)
    standard_returns = netvalue2return(standard_netvalue4list)
    fund_returns = np.array(fund_returns)
    standard_returns = np.array(standard_returns)
    excess_returns = (1 + fund_returns) / (1 + standard_returns) - 1
    return excess_returns.tolist()

def calculate_excess_one_cum_return(netvalue4list,standard_netvalue4list):
    """
    计算累计超额收益
    :param netvalue4list:
    :param standard_netvalue4list:
    :return:
    """
    excess_returns = calculate_excess_returns(netvalue4list, standard_netvalue4list)
    excess_cum_returns = returns2cumreturns(excess_returns)  # 起点是0
    return excess_cum_returns[-1]

def calculate_excess_cum_returns(netvalue4list,standard_netvalue4list):
    """
    计算累计超额收益序列
    :param netvalue4list:
    :param standard_netvalue4list:
    :return:
    """
    excess_returns = calculate_excess_returns(netvalue4list, standard_netvalue4list)
    excess_cum_returns = returns2cumreturns(excess_returns)  # 起点是0
    return excess_cum_returns

def calculate_excess_sharpe_ratio(netvalue4list, standard_netvalue4list):
    """
    超额夏普比率
    :param netvalue4list:
    :param standard_netvalue4list:
    :return:
    """
    excess_returns = calculate_excess_returns(netvalue4list, standard_netvalue4list)
    returns = netvalue2return(netvalue4list)
    return np.mean(excess_returns)/np.std(returns)

def calculate_excess_max_drawdown(netvalue4list, standard_netvalue4list):
    """
    超额最大回撤
    :param netvalue4list:
    :param standard_netvalue4list:
    :return:
    """
    excess_returns = calculate_excess_returns(netvalue4list, standard_netvalue4list)
    excess_cum_returns = returns2cumreturns(excess_returns) # 起点是0
    excess_net = [i+1 for i in excess_cum_returns]
    excess_max_drawdown = calculate_max_drawdown(excess_net)
    return excess_max_drawdown

def calculate_excess_win_rate(netvalue4list, standard_netvalue4list):
    """
    超额胜率计算
    :param netvalue4list:list
    :return:
    """
    fund_returns = netvalue2return(netvalue4list)
    standard_fund_returns = netvalue2return(standard_netvalue4list)
    num_trading_days = len(fund_returns)
    num_positive_returns = 0
    for i in range(num_trading_days):
        if fund_returns[i]>standard_fund_returns[i]:
            num_positive_returns = num_positive_returns+1
    return num_positive_returns / num_trading_days


def calculate_excess_odds_ratio(netvalue4list, standard_netvalue4list):
    """
    超额赔率
    :param netvalue4list:
    :return:
    """
    excess_returns = calculate_excess_returns(netvalue4list, standard_netvalue4list)
    negative_returns = np.mean([r for r in excess_returns if r < 0])
    positive_returns = np.mean([r for r in excess_returns if r > 0])
    odds_ratio = positive_returns / negative_returns
    return odds_ratio

# ------------------------------------------年化指标-------------------------------------------------