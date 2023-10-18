# -*- coding: UTF-8 -*-
"""
@Project ：FundInv 
@File    ：IndependentFund.py
@IDE     ：PyCharm 
@Author  ：tutu
@Date    ：2023-08-16 9:33
本文件根据全部基金（11324）求基金的共振因子，并将其分为共振基金、中立基金、独立基金，然后在跟已有的基金池merge
所用数据为重仓股数据（季度披露）
"""

# 载入包
from iFinDPy import *  # 同花顺API接口
import pandas as pd
import warnings
warnings.filterwarnings(action='ignore')  # 导入warnings模块，并指定忽略代码运行中的警告信息

def getIndependent(lastYearDate, apikey):
    """
    :param lastYearDate: 年报/半年报交易日
    :param apikey: list，["tfzq1556", "752862"]
    :return: df
    """
    # 接入同花顺API接口
    thsLogin = THS_iFinDLogin(apikey[0], apikey[1])

    try:
        HDF = pd.read_csv("input/HDF" + lastYearDate + ".csv")
        HDF.drop('Unnamed: 0', axis=1, inplace=True)
    except FileNotFoundError:
        print("本地文件不存在，尝试从接口获取数据...")
        # 获取基金代码
        # 上市股票型开放式基金
        IPOStockFund = THS_DR('p03291', 'date=' + lastYearDate + ';blockname=051001022001;iv_type=allcontract',
                              'p03291_f002:Y,p03291_f003:Y', 'format:dataframe').data.iloc[:, [0]].values.tolist()
        IPOStockFund1 = [item for sublist in IPOStockFund for item in sublist]
        # 非上市股票型开放式基金
        NoIPOStockFund = THS_DR('p03291', 'date=' + lastYearDate + ';blockname=051001022002;iv_type=allcontract',
                                'p03291_f002:Y,p03291_f003:Y', 'format:dataframe').data.iloc[:, [0]].values.tolist()
        NoIPOStockFund1 = [item for sublist in NoIPOStockFund for item in sublist]
        # 上市混合型开放式基金
        MixedIPOFund = THS_DR('p03291', 'date=' + lastYearDate + ';blockname=051001024001;iv_type=allcontract',
                              'p03291_f002:Y,p03291_f003:Y', 'format:dataframe').data.iloc[:, [0]].values.tolist()
        MixedIPOFund1 = [item for sublist in MixedIPOFund for item in sublist]
        # 非上市混合型开放式基金
        NoMixedFund = THS_DR('p03291', 'date=' + lastYearDate + ';blockname=051001024002;iv_type=allcontract',
                             'p03291_f002:Y,p03291_f003:Y', 'format:dataframe').data.iloc[:, [0]].values.tolist()
        NoMixedFund1 = [item for sublist in NoMixedFund for item in sublist]
        AllFund = IPOStockFund1 + NoIPOStockFund1 + MixedIPOFund1 + NoMixedFund1

        n = int(len(AllFund) / 1000)
        for j in range(10):
            df1 = THS_BD(AllFund[n * 1000::],
                         'ths_fund_num_of_heavily_held_sec_fund;ths_top_sec_held_num_fund',
                         lastYearDate + ',' + str(j + 1) + ';' + lastYearDate + ',' + str(j + 1)).data
            df1.rename(columns={'ths_fund_num_of_heavily_held_sec_fund': 'x' + str(j + 1),
                                'ths_top_sec_held_num_fund': 'ww' + str(j + 1)}, inplace=True)
            if j == 0:
                HDF = df1
            else:
                HDF = pd.merge(HDF, df1, on='thscode', how='left')

        for i in range(n):
            for j in range(10):
                df1 = THS_BD(AllFund[i * 1000:(i + 1) * 1000],
                             'ths_fund_num_of_heavily_held_sec_fund;ths_top_sec_held_num_fund',
                             lastYearDate + ',' + str(j + 1) + ';' + lastYearDate + ',' + str(j + 1)).data
                df1.rename(columns={'ths_fund_num_of_heavily_held_sec_fund': 'x' + str(j + 1),
                                    'ths_top_sec_held_num_fund': 'ww' + str(j + 1)}, inplace=True)
                if j == 0:
                    df2 = df1
                else:
                    df2 = pd.merge(df2, df1, on='thscode', how='left')
            HDF = pd.concat([HDF, df2])
        HDF.to_csv("input/HDF" + lastYearDate + ".csv")
    # print("基金总个数为{}".format(len(HDF)))
    HDF_cleaned = HDF.dropna()
    x_cols = ['x' + str(i + 1) for i in range(10)]
    ww_cols = ['ww' + str(i + 1) for i in range(10)]
    w_cols = ['w' + str(i + 1) for i in range(10)]
    HDF_cleaned['wwsum'] = HDF_cleaned[ww_cols].sum(axis=1)
    for i in range(10):
        HDF_cleaned['w' + str(i + 1)] = HDF_cleaned['ww' + str(i + 1)] / HDF_cleaned['wwsum']
        HDF_cleaned.drop('ww' + str(i + 1), axis=1, inplace=True)
        HDF_cleaned.reset_index()

    HDF_cleaned['H'] = HDF_cleaned['x1'] * HDF_cleaned['w1'] + HDF_cleaned['x2'] * HDF_cleaned['w2'] + HDF_cleaned[
        'x3'] * \
                       HDF_cleaned['w3'] + HDF_cleaned['x4'] * HDF_cleaned['w4'] + HDF_cleaned['x5'] * HDF_cleaned[
                           'w5'] + \
                       HDF_cleaned['x6'] * HDF_cleaned['w6'] + HDF_cleaned['x7'] * HDF_cleaned['w7'] + HDF_cleaned[
                           'x8'] * \
                       HDF_cleaned['w8'] + HDF_cleaned['x9'] * HDF_cleaned['w9'] + HDF_cleaned['x10'] * HDF_cleaned[
                           'w10']
    # HDF_cleaned['H'] = HDF_cleaned[x_cols].mul(HDF_cleaned[w_cols]).sum(axis=1)

    HDF_cleaned = HDF_cleaned.sort_values(by='H', ascending=False)
    afundnum = len(HDF_cleaned)
    Hflag1 = afundnum * (1 / 3)
    Hflag2 = afundnum * (2 / 3)
    num_resonance = int(afundnum / 3)  # 共振基金数量
    num_independent = num_resonance  # 独立基金数量
    num_neutral = afundnum - num_resonance - num_independent  # 中立基金数量
    # 将DataFrame分成不同的部分
    resonance_funds = HDF_cleaned.iloc[:num_resonance]
    neutral_funds = HDF_cleaned.iloc[num_resonance:(num_resonance + num_neutral)]
    independent_funds = HDF_cleaned.iloc[(num_resonance + num_neutral):]
    # 为每个部分分配相应的标签
    resonance_funds['HCategory'] = '共振基金'
    neutral_funds['HCategory'] = '中立基金'
    independent_funds['HCategory'] = '独立基金'
    # 合并三个部分
    result = pd.concat([resonance_funds, neutral_funds, independent_funds])
    result.to_csv("output/IndependentFund.csv")
    return result[['thscode', 'HCategory']]
