# -*- coding: UTF-8 -*-
"""
@Project ：FundInv
@File    ：shortbondfundlabel.py
@IDE     ：PyCharm
@Author  ：tutu
@Date    ：2023-10-10 14:46
"""

# 载入包
from iFinDPy import *  # 同花顺API接口
import pandas as pd
import warnings

from getfunction import getchunzhaicode

warnings.filterwarnings(action='ignore')  # 导入warnings模块，并指定忽略代码运行中的警告信息


def getfundcompany(endDate, apikey):
    """
    纯债基金基金公司标签
    :param endDate:
    :param apikey:
    :return:
    """
    chunzhai4list = getchunzhaicode()


    # 基金公司标签
    grouped_sum = cunzhai4df.groupby(['ths_fund_supervisor_fund'])['ths_mergesize_fund'].sum()
    sorted_sum = grouped_sum.sort_values(ascending=False)
    cunzhai4df['基金公司规模'] = cunzhai4df.apply(lambda row: sorted_sum.get((row['ths_fund_supervisor_fund']), default=0),
                                            axis=1)
    cunzhai4df['基金公司标签'] = '小基金公司'
    cunzhai4df.iloc[:int(len(cunzhai4df) * 0.2), cunzhai4df.columns.get_loc('基金公司标签')] = '大基金公司'
    return cunzhai4df[['thscode', '基金公司标签']]


def gettime(endDate, apikey):
    """
    纯债基金获得久期标签，三等分点
    :param endDate:
    :param apikey:
    :return:
    """
    cunzhai = pd.read_csv("output/chunzhai.csv")
    cunzhai.drop('Unnamed: 0', axis=1, inplace=True)
    cunzhai = cunzhai.sort_values(by='ths_portfolio_duration_fund', ascending=False)
    one_third = len(cunzhai) // 3
    cunzhai['久期标签'] = '中'
    cunzhai.iloc[:one_third, cunzhai.columns.get_loc('久期标签')] = '长'
    cunzhai.iloc[-one_third:, cunzhai.columns.get_loc('久期标签')] = '短'
    return cunzhai[['thscode', '久期标签']]


def getlever(endDate, apikey):
    """
    纯债基金获得杠杆比例标签，三等分点
    :param endDate:
    :param apikey:
    :return:
    """
    cunzhai = pd.read_csv("output/chunzhai.csv")
    cunzhai.drop('Unnamed: 0', axis=1, inplace=True)
    cunzhai = cunzhai.sort_values(by='ths_jjggbl_fund', ascending=False)
    one_third = len(cunzhai) // 3
    cunzhai['杠杆比例标签'] = '中'
    cunzhai.iloc[:one_third, cunzhai.columns.get_loc('杠杆比例标签')] = '大'
    cunzhai.iloc[-one_third:, cunzhai.columns.get_loc('杠杆比例标签')] = '小'
    return cunzhai[['thscode', '杠杆比例标签']]


def getbondtype(endDate, apikey):
    cunzhai = pd.read_csv("output/chunzhai.csv")
    cunzhai.drop('Unnamed: 0', axis=1, inplace=True)
    cunzhai4list = cunzhai.iloc[:, [0]].values.tolist()
    cunzhai4list = [item for sublist in cunzhai4list for item in sublist]
    cunzhai4char = ','.join(cunzhai4list)

    try:
        cunzhaiFundRatioDF = pd.read_csv("input/cunzhaiFundRatioDF" + endDate + ".csv")
        cunzhaiFundRatioDF.drop('Unnamed: 0', axis=1, inplace=True)
    except FileNotFoundError:
        print("本地文件不存在，尝试从接口获取数据...")
        frequency = 500
        n = int(len(cunzhai4list) / frequency)
        # 末期截面基础数据
        cunzhaiFundRatioDF = THS_DR('p00483', 'bgqlb=' + endDate + ';jjlb=' + ','.join(cunzhai4list[n * frequency::]),
                                    'jydm:Y,jydm_mc:Y,p00483_f002:Y,p00483_f007:Y,p00483_f008:Y',
                                    'format:dataframe').data
        for i in range(n):
            df1 = THS_DR('p00483',
                         'bgqlb=' + endDate + ';jjlb=' + ','.join(cunzhai4list[i * frequency:(i + 1) * frequency]),
                         'jydm:Y,jydm_mc:Y,p00483_f002:Y,p00483_f007:Y,p00483_f008:Y', 'format:dataframe').data
            cunzhaiFundRatioDF = pd.concat([cunzhaiFundRatioDF, df1])
        cunzhaiFundRatioDF.to_csv("input/cunzhaiFundRatioDF" + endDate + ".csv")

    cunzhaiFundRatioDF.rename(columns={'p00483_f002': 'thscode', 'p00483_f008': 'ratio'}, inplace=True)
    cunzhaiFundRatioDF['ratio_num'] = pd.to_numeric(cunzhaiFundRatioDF['ratio'], errors='coerce')
    bond4list = cunzhaiFundRatioDF['thscode'].dropna().unique().tolist()
    bondcode4df = THS_toTHSCODE(','.join(bond4list),
                                'mode:seccode;sectype:002,002001,002003,002005,002006,002007,002007001,002007002,002007003,002007004,002007005,002007006,002008,002009,002010,002010001,002010002,002010003,002010004,002010005,002010006,002010007,002010008,002012,002015,002018,002020,002021,002022,002023,002024;;tradestatus:2;isexact:0').data
    bondcode4df['first_code'] = bondcode4df['thscode'].str.split(',').str[0]
    bondcode4list = bondcode4df.iloc[:, [2]].values.tolist()
    bondcode4list = [item for sublist in bondcode4list for item in sublist]
    cunzhai4char = ','.join(bondcode4list)
    bond4df = THS_BD(cunzhai4char, 'ths_ths_bond_first_type_bond', '').data
    # 合并
    cunzhaiFundRatioDF.rename(columns={'thscode': 'seccode'}, inplace=True)
    bondcode4df.rename(columns={'thscode': 'allcode', 'first_code': 'thscode'}, inplace=True)
    bondcode4df = pd.merge(bondcode4df, bond4df, on='thscode', how='left')
    cunzhaiFundRatioDF = pd.merge(cunzhaiFundRatioDF, bondcode4df, on='seccode', how='left')
    bondtypes = bond4df['ths_ths_bond_first_type_bond'].dropna().unique().tolist()

    # 分类为利率债和信用债
    def generate_new_bond_type(row):
        if row['ths_ths_bond_first_type_bond'] in ['国债', '地方政府债', '政府支持机构债']:
            return '利率债'
        else:
            return '信用债'

    cunzhaiFundRatioDF['bondfundtype'] = cunzhaiFundRatioDF.apply(generate_new_bond_type, axis=1)

    result = cunzhaiFundRatioDF.groupby(['jydm', 'bondfundtype'])['ratio_num'].sum().reset_index()
    result = result.loc[result.groupby('jydm')['ratio_num'].idxmax()]
    result = result.sort_values(by='ratio_num', ascending=False)
    result.rename(columns={'jydm': 'thscode'}, inplace=True)
    return result[['thscode', 'bondfundtype']]


def getdingkai(endDate, apikey):
    """
    获取定开指标,1表示定开，0表示非定开
    :param endDate:
    :param apikey:
    :return:
    """
    cunzhai = pd.read_csv("output/chunzhai.csv")
    cunzhai.drop('Unnamed: 0', axis=1, inplace=True)
    cunzhai['是否为定开'] = cunzhai['ths_fund_short_name_fund'].str.contains("定开").astype(int)
    return cunzhai[['thscode', '是否为定开']]
