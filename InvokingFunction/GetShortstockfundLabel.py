# -*- coding: UTF-8 -*-
"""
@Project ：FundInv 
@File    ：GetShortstockfundLabel.py
@IDE     ：PyCharm 
@Author  ：tutu
@Date    ：2023-08-18 10:53
股票基金的短期标签
"""

# 载入包
import pandas as pd
import numpy as np
import warnings

from InvokingFunction.GetData import GetstockindustryData, GetsfundastockData, GetstockstyleData, Getsfund10stockData, \
    Getsfund10sumstockData
from InvokingFunction.GetGFunction import getstockfundcode, exchangedate1
from InvokingFunction.GetSFunction import getstock1industry, find_nearest_below1, find_nearest_above1

warnings.filterwarnings(action='ignore')  # 导入warnings模块，并指定忽略代码运行中的警告信息


def getindustry(lastYearDate, apikey):
    """
    获得股票基金短期的行业主题标签
    :param lastYearDate:年报/半年报
    :param apikey:
    :return:
    """
    # 获取股票的行业分类数据
    aStockIndDF = GetstockindustryData(lastYearDate, apikey)
    aStockIndDF = getstock1industry(aStockIndDF)

    # 获取基金池权益持仓数据
    fundcode4list = getstockfundcode()
    FundRatioDF = GetsfundastockData(fundcode4list, lastYearDate, apikey)
    FundRatioDF.rename(columns={'p00475_f002': 'thscode', 'p00475_f009': 'ratio'}, inplace=True)
    FundRatioDF['ratio_num'] = pd.to_numeric(FundRatioDF['ratio'], errors='coerce')
    FundRatioDF = pd.merge(FundRatioDF, aStockIndDF, on='thscode', how='left')

    # 分组求和
    result = FundRatioDF.groupby(['jydm', 'IND'])['ratio_num'].sum().reset_index()
    result = result.loc[result.groupby('jydm')['ratio_num'].idxmax()]
    result = result.sort_values(by='ratio_num', ascending=False)

    def generate_new_value(row):
        if row['ratio_num'] > 60:
            return row['IND'] + "行业基金"
        else:
            return '行业均衡基金'

    result['INDtype'] = result.apply(generate_new_value, axis=1)
    # print('{}行业标签成功匹配的基金比例为：{}/{}'.format(lastYearDate,len(result), len(MyFundList)))
    result.rename(columns={'jydm': 'thscode'}, inplace=True)
    return result[['thscode', 'INDtype']]


def getstyle(lastYearDate, apikey):
    """
    获得股票基金短期的风格标签
    :param lastYearDate:年报/半年报
    :param apikey: list
    :return: 无返回，输出从csv文件
    """
    aStockInfoDF = GetstockstyleData(lastYearDate, apikey)

    missing_values_count = aStockInfoDF.isnull().sum(axis=1)
    rows_with_missing = missing_values_count[missing_values_count > 0]
    print("{}存在缺失值的行数为：{}".format(lastYearDate, len(rows_with_missing)))
    # 用行业均值替换缺失值
    aStockInfoDF['ths_the_citic_industry_stock'] = aStockInfoDF['ths_the_citic_industry_stock'].fillna('其他')
    means = aStockInfoDF.iloc[:, 1::].groupby('ths_the_citic_industry_stock').mean()
    for col in aStockInfoDF.columns[1:-1]:
        aStockInfoDF[col].fillna(aStockInfoDF['ths_the_citic_industry_stock'].map(means[col]), inplace=True)

    # 划分大中小盘，前200只为大盘股，200-500为中盘，剩下的为小盘股
    StockInfoDF = aStockInfoDF.sort_values(by='ths_market_value_stock', ascending=False).reset_index(drop=True)
    StockInfoDF['Flag'] = 'Small'
    StockInfoDF.loc[:199, 'Flag'] = 'Big'
    StockInfoDF.loc[200:499, 'Flag'] = 'Mid'

    StockInfoDF['LMT'] = StockInfoDF.loc[199, 'ths_market_value_stock']
    StockInfoDF['MST'] = StockInfoDF.loc[499, 'ths_market_value_stock']

    # 计算价值得分
    StockInfoDF['BP'] = 1 / StockInfoDF['ths_pb_latest_stock']
    StockInfoDF['EPTTM'] = 1 / StockInfoDF['ths_pe_ttm_stock']
    StockInfoDF['SPTTM'] = 1 / StockInfoDF['ths_ps_ttm_stock']

    StockInfoDF['BP1'] = StockInfoDF.groupby('Flag')['BP'].rank(method='first')
    StockInfoDF['EPTTM1'] = StockInfoDF.groupby('Flag')['EPTTM'].rank(method='first')
    StockInfoDF['SPTTM1'] = StockInfoDF.groupby('Flag')['SPTTM'].rank(method='first')
    weightOVS = [0.5, 0.25, 0.25]
    StockInfoDF['OVS'] = StockInfoDF['BP1'] * weightOVS[0] + StockInfoDF['EPTTM1'] * weightOVS[1] + StockInfoDF[
        'SPTTM1'] * weightOVS[2]

    # 计算成长得分
    StockInfoDF['NETPROFITINCYOY'] = StockInfoDF['ths_sq_np_yoy_stock'] * 0.01
    StockInfoDF['OPERREVINCYOY'] = StockInfoDF['ths_revenue_yoy_sq_stock'] * 0.01
    StockInfoDF['OPERPROFITINCYOY'] = StockInfoDF['ths_op_yoy_sq_stock'] * 0.01

    StockInfoDF['NETPROFITINCYOY1'] = StockInfoDF.groupby('Flag')['NETPROFITINCYOY'].rank(method='first')
    StockInfoDF['OPERREVINCYOY1'] = StockInfoDF.groupby('Flag')['OPERREVINCYOY'].rank(method='first')
    StockInfoDF['OPERPROFITINCYOY1'] = StockInfoDF.groupby('Flag')['OPERPROFITINCYOY'].rank(method='first')
    weightOGS = [0.33, 0.33, 0.33]
    StockInfoDF['OGS'] = StockInfoDF['NETPROFITINCYOY1'] * weightOGS[0] + StockInfoDF['OPERREVINCYOY1'] * weightOGS[1] + \
                         StockInfoDF['OPERPROFITINCYOY1'] * weightOGS[2]

    # 成长价值综合得分和门限值
    StockInfoDF['VCG'] = StockInfoDF['OGS'] - StockInfoDF['OVS']
    StockInfoDF = StockInfoDF.sort_values(by=['Flag', 'VCG'], ascending=[False, False])
    StockInfoDF['CumSum'] = StockInfoDF.groupby('Flag')['ths_market_value_stock'].cumsum()
    divisors = StockInfoDF.groupby('Flag')['ths_market_value_stock'].sum()

    def custom_divide(row):
        if row['Flag'] == 'Big':
            return row['CumSum'] / divisors['Big']
        elif row['Flag'] == 'Mid':
            return row['CumSum'] / divisors['Mid']
        else:
            return row['CumSum'] / divisors['Small']

    StockInfoDF['CumRatio'] = StockInfoDF.apply(custom_divide, axis=1)

    # 分组并找出门限值
    result3 = StockInfoDF.groupby('Flag').apply(find_nearest_below1, target_ratio=0.33, cum_col='CumRatio',
                                                flag_col='VCG')
    StockInfoDF['GT_Flag'] = StockInfoDF['Flag'].map(result3)
    result4 = StockInfoDF.groupby('Flag').apply(find_nearest_above1, target_ratio=0.67, cum_col='CumRatio',
                                                flag_col='VCG')
    StockInfoDF['VT_Flag'] = StockInfoDF['Flag'].map(result4)

    # 计算股票在风格箱中的定位
    StockInfoDF['rawX'] = 100 * (
            1 + (StockInfoDF['VCG'] - StockInfoDF['VT_Flag']) / (StockInfoDF['GT_Flag'] - StockInfoDF['VT_Flag']))
    StockInfoDF['rawY'] = 100 * (1 + (np.log(StockInfoDF['ths_market_value_stock']) - np.log(StockInfoDF['MST'])) / (
            np.log(StockInfoDF['LMT']) - np.log(StockInfoDF['MST'])))

    # 对我的基金池进行风格主题分类
    fundcode4list = getstockfundcode()
    FundRatioDF = GetsfundastockData(fundcode4list, lastYearDate, apikey)  # 获取基金权益明细的数据
    FundRatioDF.rename(columns={'p00475_f002': 'thscode', 'p00475_f009': 'ratio'}, inplace=True)
    FundRatioDF['ratio_num'] = pd.to_numeric(FundRatioDF['ratio'], errors='coerce')
    FundRatioDF['ratio_num'] = FundRatioDF['ratio_num'] / 100
    FundRatioDF = pd.merge(FundRatioDF, StockInfoDF[['thscode', 'rawX', 'rawY']], on='thscode', how='left')
    FundRatioDF['FrawX'] = FundRatioDF['rawX'] * FundRatioDF['ratio_num']
    FundRatioDF['FrawY'] = FundRatioDF['rawY'] * FundRatioDF['ratio_num']

    # 计算基金在风格箱中的定位
    result = FundRatioDF.groupby(['jydm'])[['FrawX', 'FrawY']].sum()

    def style_divide2(row, num1=100, num2=200):
        if row['FrawY'] < num1:
            return "小盘"
        elif num1 <= row['FrawY'] <= num2:
            return "中盘"
        else:
            return "大盘"

    result = result.sort_values(by='FrawX', ascending=False)
    one_fifth = len(result) // 5
    result['Xstyle'] = '均衡型'
    result.iloc[:one_fifth, result.columns.get_loc('Xstyle')] = '成长型'
    result.iloc[one_fifth:(2 * one_fifth), result.columns.get_loc('Xstyle')] = '成长-均衡型'
    result.iloc[(one_fifth * 3):(4 * one_fifth), result.columns.get_loc('Xstyle')] = '均衡-价值型'
    result.iloc[-one_fifth:, result.columns.get_loc('Xstyle')] = '价值型'

    result['Ystyle'] = result.apply(style_divide2, axis=1)
    print('{}风格标签成功匹配的基金比例为：{}/{}'.format(lastYearDate, len(result), len(fundcode4list)))
    result.reset_index(drop=False, inplace=True)
    result.rename(columns={'jydm': 'thscode'}, inplace=True)
    return result[['thscode', 'Xstyle', 'Ystyle']]


def getindependent(lastQuarDate, apikey):
    """
    :param lastQuarDate: 季报
    :param apikey:
    :return: df
    """
    fundcode4list = getstockfundcode()
    HDF = Getsfund10stockData(fundcode4list, lastQuarDate, apikey)

    # HDF = HDF.dropna()
    ww_cols = ['ww' + str(i + 1) for i in range(10)]
    HDF['wwsum'] = HDF[ww_cols].sum(axis=1)
    for i in range(10):
        HDF['w' + str(i + 1)] = HDF['ww' + str(i + 1)] / HDF['wwsum']
        HDF.drop('ww' + str(i + 1), axis=1, inplace=True)
        HDF.reset_index()

    HDF['H'] = HDF['x1'] * HDF['w1'] + HDF['x2'] * HDF['w2'] + HDF['x3'] * HDF['w3'] + HDF['x4'] * HDF['w4'] + HDF[
        'x5'] * HDF['w5'] + HDF['x6'] * HDF['w6'] + HDF['x7'] * HDF['w7'] + HDF['x8'] * HDF['w8'] + HDF['x9'] * HDF[
        'w9'] + HDF['x10'] * HDF['w10']
    # HDF['H'] = HDF[x_cols].mul(HDF[w_cols]).sum(axis=1)

    HDF = HDF.sort_values(by='H', ascending=False)
    afundnum = len(HDF)
    num_resonance = int(afundnum / 3)  # 共振基金数量
    num_independent = num_resonance  # 独立基金数量
    num_neutral = afundnum - num_resonance - num_independent  # 中立基金数量
    # 将DataFrame分成不同的部分
    resonance_funds = HDF.iloc[:num_resonance]
    neutral_funds = HDF.iloc[num_resonance:(num_resonance + num_neutral)]
    independent_funds = HDF.iloc[(num_resonance + num_neutral):]
    # 为每个部分分配相应的标签
    resonance_funds['HCategory'] = '共振基金'
    neutral_funds['HCategory'] = '中立基金'
    independent_funds['HCategory'] = '独立基金'
    # 合并三个部分
    result = pd.concat([resonance_funds, neutral_funds, independent_funds])
    return result[['thscode', 'HCategory']]


def getCR(lastQuarDate, apikey):
    """
    :param lastQuarDate: 季报
    :param apikey: list，["tfzq1556", "752862"]
    :return: df
    """
    fundcode4list = getstockfundcode()
    CR4df = Getsfund10sumstockData(fundcode4list, lastQuarDate, apikey)
    CR4df = CR4df.sort_values(by='ths_top_n_top_stock_mv_to_si_mv_fund', ascending=False)
    one_third = len(CR4df) // 3
    CR4df['cr'] = '中'
    CR4df.iloc[:one_third, CR4df.columns.get_loc('cr')] = '高'
    CR4df.iloc[-one_third:, CR4df.columns.get_loc('cr')] = '低'
    return CR4df[['thscode', 'cr']]

