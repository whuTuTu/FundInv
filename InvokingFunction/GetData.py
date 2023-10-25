# -*- coding: UTF-8 -*-
"""
@Project :FundInv
@File    :GetData.py
@IDE     :Pycharm
@Author  :tutu
@Date    :2023/10/22 21:03
# 用于储存用api接口提取数据的函数
"""
# 载入包
import pandas as pd
from iFinDPy import *  # 同花顺API接口
import os
import warnings
from InvokingFunction.GetFunction import exchangedate1, df2list
warnings.filterwarnings(action='ignore')  # 导入warnings模块，并指定忽略代码运行中的警告信息

# 更改相对路径
path = "D:\TFCode\FundInv"
os.chdir(path)

# -----------------------------------------------获取债券相关数据-----------------------------------------------
def GetbondTHScode(fundcode4list):
    """
    将没有后缀的债券代码变成有后缀名的债券代码
    :param fundcode4list:
    :return: df
    """
    bond4df = THS_toTHSCODE(','.join(fundcode4list),
                  'mode:seccode;sectype:002,002001,002003,002005,002006,002007,002007001,002007002,002007003,'
                  '002007004,002007005,002007006,002008,002009,002010,002010001,002010002,002010003,002010004,'
                  '002010005,002010006,002010007,002010008,002012,002015,002018,002020,002021,002022,002023,'
                  '002024;;tradestatus:2;isexact:0').data
    return bond4df

# -----------------------------------------------获取债券基金相关数据-----------------------------------------------
def GetbondType(bondcode4list, HYDate, apikey):
    """
    获取债券类型
    :param bondcode4list:
    :param apikey:
    :return:
    """
    thsLogin = THS_iFinDLogin(apikey[0], apikey[1])
    try:
        bond4df = pd.read_csv("input/BondData/Type/HYType" + HYDate + ".csv")
        bond4df.drop('Unnamed: 0', axis=1, inplace=True)
    except FileNotFoundError:
        print("本地文件不存在，尝试从接口获取数据...")
        bond4df = THS_BD(','.join(bondcode4list), 'ths_ths_bond_first_type_bond', '').data
        bond4df.to_csv("input/BondData/Type/HYType" + HYDate + ".csv")
    return bond4df

def GetbfundbasicData(QDate, apikey):
    """
    获取债券基金初筛的全市场数据
    :param QDate:20200630的格式
    :param apikey:
    :return:
    """
    thsLogin = THS_iFinDLogin(apikey[0], apikey[1])
    try:
        AllFundDF = pd.read_csv("input/BondFundData/Basic/Qbasic" + QDate + ".csv")
        AllFundDF.drop('Unnamed: 0', axis=1, inplace=True)
    except FileNotFoundError:
        print("本地文件不存在，尝试从接口获取数据...")
        # 获取基金代码
        # 上市债券型开放式基金
        IPOBondFund = THS_DR('p03291', 'date=' + QDate + ';blockname=051001023001;iv_type=allcontract',
                             'p03291_f002:Y,p03291_f003:Y', 'format:dataframe').data
        IPOBondFund1 = df2list(IPOBondFund.iloc[:, [0]])
        # 非上市债券型开放式基金
        NoIPOBondFund = THS_DR('p03291', 'date=' + QDate + ';blockname=051001023002;iv_type=allcontract',
                               'p03291_f002:Y,p03291_f003:Y', 'format:dataframe').data
        NoIPOBondFund1 = df2list(NoIPOBondFund.iloc[:, [0]])
        # 获取全部数据并保存为csv文件
        AllFund = IPOBondFund1 + NoIPOBondFund1
        n = int(len(AllFund) / 1000)
        # 末期截面基础数据
        AllFundDF = THS_BD(AllFund[n * 1000::],
                           'ths_fund_code_fund;ths_fund_short_name_fund;ths_fund_supervisor_fund'
                           ';ths_fund_manager_current_fund;ths_invest_type_second_classi_fund;ths_mergesize_fund',
                           ';;;;;' + exchangedate1(QDate)).data
        for i in range(n):
            df1 = THS_BD(AllFund[i * 1000:(i + 1) * 1000],
                         'ths_fund_code_fund;ths_fund_short_name_fund;ths_fund_supervisor_fund'
                           ';ths_fund_manager_current_fund;ths_invest_type_second_classi_fund;ths_mergesize_fund',
                           ';;;;;' + exchangedate1(QDate)).data
            AllFundDF = pd.concat([AllFundDF, df1])
        AllFundDF.to_csv("input/BondFundData/Basic/Qbasic" + QDate + ".csv")

    AllFundDF = pd.read_csv("input/BondFundData/Basic/Qbasic" + QDate + ".csv")
    AllFundDF.drop('Unnamed: 0', axis=1, inplace=True)

    return AllFundDF

def GetbfundcompanyData(fundcode4list, QDate, apikey):
    """
    获取债基对应的基金公司和基金规模（合并）
    :param fundcode4list:
    :param QDate:
    :param apikey:
    :return:
    """
    thsLogin = THS_iFinDLogin(apikey[0], apikey[1])
    try:
        fund4df = pd.read_csv("input/BondFundData/Company/Qcompany" + QDate + ".csv")
        fund4df.drop('Unnamed: 0', axis=1, inplace=True)
    except FileNotFoundError:
        print("本地文件不存在，尝试从接口获取数据...")
        fund4df = THS_BD(fundcode4list, 'ths_fund_supervisor_fund;ths_mergesize_fund',
                         ';' + exchangedate1(QDate)).data
        fund4df.to_csv("input/BondFundData/Company/Qcompany" + QDate + ".csv")
    return fund4df


def GetbfunddurationData(fundcode4list, QDate, apikey):
    """
    获取债基对应的久期
    :param fundcode4list:
    :param QDate:
    :param apikey:
    :return:
    """
    thsLogin = THS_iFinDLogin(apikey[0], apikey[1])
    try:
        fund4df = pd.read_csv("input/BondFundData/Duration/Qtime" + QDate + ".csv")
        fund4df.drop('Unnamed: 0', axis=1, inplace=True)
    except FileNotFoundError:
        print("本地文件不存在，尝试从接口获取数据...")
        fund4df = THS_BD(fundcode4list, 'ths_portfolio_duration_fund', exchangedate1(QDate)).data
        fund4df.to_csv("input/BondFundData/Duration/Qtime" + QDate + ".csv")
    return fund4df


def GetbfundleverData(fundcode4list, QDate, apikey):
    """
    获取债基对应的杠杆率
    :param fundcode4list:
    :param QDate:
    :param apikey:
    :return:
    """
    thsLogin = THS_iFinDLogin(apikey[0], apikey[1])
    try:
        fund4df = pd.read_csv("input/BondFundData/Lever/Qlever" + QDate + ".csv")
        fund4df.drop('Unnamed: 0', axis=1, inplace=True)
    except FileNotFoundError:
        print("本地文件不存在，尝试从接口获取数据...")
        fund4df = THS_BD(fundcode4list, 'ths_jjggbl_fund', exchangedate1(QDate)).data
        fund4df.to_csv("input/BondFundData/Lever/Qlever" + QDate + ".csv")
    return fund4df

def GetbfundbondData(fundcode4list, HYDate, apikey):
    """
    获取债基的债券持仓数据
    :param fundcode4list:
    :param HYDate:
    :param apikey:
    :return:
    """
    thsLogin = THS_iFinDLogin(apikey[0], apikey[1])
    try:
        fund4df = pd.read_csv("input/BondFundData/Bond/HYBond" + HYDate + ".csv")
        fund4df.drop('Unnamed: 0', axis=1, inplace=True)
    except FileNotFoundError:
        print("本地文件不存在，尝试从接口获取数据...")
        frequency = 500
        n = int(len(fundcode4list) / frequency)
        # 末期截面基础数据
        fund4df = THS_DR('p00483', 'bgqlb=' + HYDate + ';jjlb=' + ','.join(fundcode4list[n * frequency::]),
                         'jydm:Y,jydm_mc:Y,p00483_f002:Y,p00483_f007:Y,p00483_f008:Y',
                         'format:dataframe').data
        for i in range(n):
            df1 = THS_DR('p00483',
                         'bgqlb=' + HYDate + ';jjlb=' + ','.join(fundcode4list[i * frequency:(i + 1) * frequency]),
                         'jydm:Y,jydm_mc:Y,p00483_f002:Y,p00483_f007:Y,p00483_f008:Y', 'format:dataframe').data
            fund4df = pd.concat([fund4df, df1])
        fund4df.to_csv("input/BondFundData/Bond/HYBond" + HYDate + ".csv")
    return fund4df

def GetbfundnetvalueData(fundcode4list, StartDate, EndDate, apikey):
    """
    每半年获取一次基金净值数据
    :param fundcode4list:
    :param StartDate: 20200630的格式
    :param EndDate:
    :param apikey:
    :return:
    """
    thsLogin = THS_iFinDLogin(apikey[0], apikey[1])
    try:
        NetValue = pd.read_csv("input/BondFundData/NetValue/HYNetValue" + StartDate + '-' + EndDate + ".csv")
        # NetValue.set_index('time', inplace=True)
    except FileNotFoundError:
        # 一段一段获取数据
        print("本地文件不存在，尝试从接口获取数据...")
        date1 = exchangedate1(StartDate)
        date2 = exchangedate1(EndDate)

        frequency = 500
        n = int(len(fundcode4list) / frequency)
        # 末期截面基础数据
        NetValue_long = THS_HQ(','.join(fundcode4list[n * frequency::]),'accumulatedNAV','CPS:3',date1,date2).data
        for j in range(n):
            df1 = THS_HQ(','.join(fundcode4list[j * frequency:(j + 1) * frequency]),'accumulatedNAV','CPS:3',date1,date2).data
            NetValue_long = pd.concat([NetValue_long, df1])

        NetValue = NetValue_long.pivot(index='time', columns='thscode', values='accumulatedNAV')
        NetValue.to_csv("input/BondFundData/NetValue/HYNetValue" + StartDate + '-' + EndDate + ".csv")
        NetValue = pd.read_csv("input/BondFundData/NetValue/HYNetValue" + StartDate + '-' + EndDate + ".csv")
        # NetValue.set_index('time', inplace=True)
    return NetValue

def GetindexcloseData(onecode4char, StartDate, EndDate, apikey):
    """
    获取某一个指数的收盘价
    :param onecode4char:
    :param StartDate:
    :param EndDate:
    :param apikey:
    :return:
    """
    thsLogin = THS_iFinDLogin(apikey[0], apikey[1])
    try:
        index4df = pd.read_csv("input/Index/HY"+onecode4char+"/HY" + StartDate + '-' + EndDate + ".csv")
        index4df.drop('Unnamed: 0', axis=1, inplace=True)
        # index4df.set_index('time', inplace=True)
    except FileNotFoundError:
        print("本地文件不存在，尝试从接口获取数据...")
        date1 = exchangedate1(StartDate)
        date2 = exchangedate1(EndDate)
        index4df = THS_HQ(onecode4char, 'close', 'CPS:3', date1, date2).data
        index4df.to_csv("input/Index/HY"+onecode4char+"/HY" + StartDate + '-' + EndDate + ".csv")
        index4df = pd.read_csv("input/Index/HY"+onecode4char+"/HY" + StartDate + '-' + EndDate + ".csv")
        # index4df.set_index('time', inplace=True)
    return index4df
# -----------------------------------------------获取股票基金相关数据-----------------------------------------------

