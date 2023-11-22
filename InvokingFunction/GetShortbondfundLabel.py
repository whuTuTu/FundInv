# -*- coding: UTF-8 -*-
"""
@Project ：FundInv
@File    ：GetShortbondfundLabel.py
@IDE     ：PyCharm
@Author  ：tutu
@Date    ：2023-10-10 14:46
"""

# 载入包
from iFinDPy import *  # 同花顺API接口
import pandas as pd
import warnings
import os
from InvokingFunction.GetData import GetbfundcompanyData, GetbfunddurationData, GetbfundleverData, GetbfundbondData, \
    GetbondTHScode, GetbondType, GetbfundtyepData
from InvokingFunction.GetGFunction import getchunzhaicode, df2list
warnings.filterwarnings(action='ignore')  # 导入warnings模块，并指定忽略代码运行中的警告信息
# 更改相对路径
path = "D:\TFCode\FundInv"
os.chdir(path)

def getfundcompany(endDate, apikey):
    """
    纯债基金基金公司标签
    :param endDate:
    :param apikey:
    :return:
    """
    chunzhai4list = getchunzhaicode()
    chunzhai4df = GetbfundcompanyData(chunzhai4list, endDate, apikey)
    # 基金公司标签
    grouped_sum = chunzhai4df.groupby(['ths_fund_supervisor_fund'])['ths_mergesize_fund'].sum()
    sorted_sum = grouped_sum.sort_values(ascending=False)
    chunzhai4df['基金公司规模'] = chunzhai4df.apply(
        lambda row: sorted_sum.get((row['ths_fund_supervisor_fund']), default=0),
        axis=1)
    chunzhai4df['基金公司标签'] = '小基金公司'
    chunzhai4df.iloc[:int(len(chunzhai4df) * 0.2), chunzhai4df.columns.get_loc('基金公司标签')] = '大基金公司'
    return chunzhai4df[['thscode', '基金公司标签']]


def getduration(endDate, apikey):
    """
    纯债基金获得久期标签，三等分点
    :param endDate:
    :param apikey:
    :return:
    """
    chunzhai4list = getchunzhaicode()
    chunzhai4df = GetbfunddurationData(chunzhai4list, endDate, apikey)

    chunzhai4df = chunzhai4df.sort_values(by='ths_portfolio_duration_fund', ascending=False)
    one_third = len(chunzhai4df) // 3
    chunzhai4df['久期标签'] = '中'
    chunzhai4df.iloc[:one_third, chunzhai4df.columns.get_loc('久期标签')] = '长'
    chunzhai4df.iloc[-one_third:, chunzhai4df.columns.get_loc('久期标签')] = '短'
    return chunzhai4df[['thscode', '久期标签']]

def getlever(endDate, apikey):
    """
    纯债基金获得杠杆比例标签，三等分点
    :param endDate:
    :param apikey:
    :return:
    """
    chunzhai4list = getchunzhaicode()
    chunzhai4df = GetbfundleverData(chunzhai4list, endDate, apikey)

    chunzhai4df = chunzhai4df.sort_values(by='ths_jjggbl_fund', ascending=False)
    one_third = len(chunzhai4df) // 3
    chunzhai4df['杠杆比例标签'] = '中'
    chunzhai4df.iloc[:one_third, chunzhai4df.columns.get_loc('杠杆比例标签')] = '大'
    chunzhai4df.iloc[-one_third:, chunzhai4df.columns.get_loc('杠杆比例标签')] = '小'
    return chunzhai4df[['thscode', '杠杆比例标签']]

def getbondtype(endDate, apikey):
    """
    纯债基金通过底层持仓获取利率债和信用债标签
    :param endDate:
    :param apikey:
    :return:
    """
    chunzhai4list = getchunzhaicode()
    cunzhaiFundRatioDF = GetbfundtyepData(chunzhai4list,endDate, apikey)  # 获取数据
    cunzhaiFundRatioDF['利率债比例'] = cunzhaiFundRatioDF['ths_nb_mv_to_bond_invest_mv_fund']+cunzhaiFundRatioDF['ths_zcxjrzszzzqtzszb_fund']+cunzhaiFundRatioDF['ths_cbb_to_bond_invest_mv_fund']
    cunzhaiFundRatioDF['bondfundtype'] = cunzhaiFundRatioDF.apply(lambda x: '利率债' if x['利率债比例'] >= 50 else '信用债', axis=1)
    return cunzhaiFundRatioDF[['thscode', 'bondfundtype']]

def getbondtype4feiqi(endDate, apikey):
    """
    （废弃）
    纯债基金通过底层持仓获取利率债和信用债标签
    :param endDate:
    :param apikey:
    :return:
    """
    chunzhai4list = getchunzhaicode()
    cunzhaiFundRatioDF = GetbfundbondData(chunzhai4list, endDate, apikey)  # 获取数据
    cunzhaiFundRatioDF.rename(columns={'p00483_f002': 'thscode', 'p00483_f008': 'ratio'}, inplace=True)
    cunzhaiFundRatioDF['ratio_num'] = pd.to_numeric(cunzhaiFundRatioDF['ratio'], errors='coerce')
    bond4list = cunzhaiFundRatioDF['thscode'].dropna().unique().tolist()
    bondcode4df = GetbondTHScode(bond4list)  # THS债券代码转换为有后缀
    bondcode4df['first_code'] = bondcode4df['thscode'].str.split(',').str[0]
    bondcode4list = df2list(bondcode4df.iloc[:, [2]])
    bond4df = GetbondType(bondcode4list, endDate, apikey)  # 获取债券对应的分类数据

    # 合并
    cunzhaiFundRatioDF.rename(columns={'thscode': 'seccode'}, inplace=True)
    bondcode4df.rename(columns={'thscode': 'allcode', 'first_code': 'thscode'}, inplace=True)
    bondcode4df = pd.merge(bondcode4df, bond4df, on='thscode', how='left')
    cunzhaiFundRatioDF = pd.merge(cunzhaiFundRatioDF, bondcode4df, on='seccode', how='left') # 合并数据

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
    result = result[result['thscode'].isin(chunzhai4list)]
    return result[['thscode', 'bondfundtype','ratio_num']]

def getdingkai():
    """
    获取定开指标,1表示定开，0表示非定开，不需要时间形参
    :param endDate:
    :param apikey:
    :return:
    """
    chunzhai = pd.read_csv("output/ChunzhaiFund/chunzhai_filter.csv")
    chunzhai.drop('Unnamed: 0', axis=1, inplace=True)
    pattern = re.compile("定开|定期开放|定期")
    chunzhai['是否为定开'] = chunzhai['ths_fund_short_name_fund'].str.contains(pattern).astype(int)
    return chunzhai[['thscode', '是否为定开']]

def getbondtype4test(endDate, apikey):
    """
    测试用
    :param endDate:
    :param apikey:
    :return:
    """
    chunzhai4list = getchunzhaicode()
    cunzhaiFundRatioDF = GetbfundbondData(chunzhai4list, endDate, apikey)  # 获取数据
    cunzhaiFundRatioDF.rename(columns={'p00483_f002': 'thscode', 'p00483_f008': 'ratio'}, inplace=True)
    cunzhaiFundRatioDF['ratio_num'] = pd.to_numeric(cunzhaiFundRatioDF['ratio'], errors='coerce')
    bond4list = cunzhaiFundRatioDF['thscode'].dropna().unique().tolist()
    bondcode4df = GetbondTHScode(bond4list)  # THS债券代码转换为有后缀
    bondcode4df['first_code'] = bondcode4df['thscode'].str.split(',').str[0]
    bondcode4list = df2list(bondcode4df.iloc[:, [2]])
    bond4df = GetbondType(bondcode4list, endDate, apikey)  # 获取债券对应的分类数据

    # 合并
    cunzhaiFundRatioDF.rename(columns={'thscode': 'seccode'}, inplace=True)
    bondcode4df.rename(columns={'thscode': 'allcode', 'first_code': 'thscode'}, inplace=True)
    bondcode4df = pd.merge(bondcode4df, bond4df, on='thscode', how='left')
    cunzhaiFundRatioDF = pd.merge(cunzhaiFundRatioDF, bondcode4df, on='seccode', how='left') # 合并数据

    result = cunzhaiFundRatioDF.groupby(['jydm',])['ratio_num'].sum().reset_index()
    result = result.sort_values(by='ratio_num', ascending=False)
    return result[['jydm','ratio_num']]