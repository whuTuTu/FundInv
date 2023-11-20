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
from InvokingFunction.GetGFunction import exchangedate1, df2list

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
    bond4df = THS_toTHSCODE(','.join(fundcode4list),'mode:seccode;sectype:002,002001,002003,002005,002006,002007,002007001,002007002,002007003,002007004,002007005,002007006,002008,002009,002010,002010001,002010002,002010003,002010004,002010005,002010006,002010007,002010008,002012,002015,002018,002020,002021,002022,002023,002024;;tradestatus:2;isexact:0').data
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
                           ';ths_fund_manager_current_fund;ths_invest_type_second_classi_fund;ths_mergesize_fund;ths_found_years_fund',
                           ';;;;;' + exchangedate1(QDate)+";"+ exchangedate1(QDate)).data
        for i in range(n):
            df1 = THS_BD(AllFund[i * 1000:(i + 1) * 1000],
                         'ths_fund_code_fund;ths_fund_short_name_fund;ths_fund_supervisor_fund'
                         ';ths_fund_manager_current_fund;ths_invest_type_second_classi_fund;ths_mergesize_fund;ths_found_years_fund',
                         ';;;;;' + exchangedate1(QDate)+";"+exchangedate1(QDate)).data
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

def GetbfundtyepData(fundcode4list,QDate, apikey):
    """
    获取债券基金的券种比例
    :param fundcode4list:
    :param QDate:
    :param apikey:
    :return:
    """
    thsLogin = THS_iFinDLogin(apikey[0], apikey[1])
    try:
        fund4df = pd.read_csv("input/BondFundData/Bond/Qbondtype" + QDate + ".csv")
        fund4df.drop('Unnamed: 0', axis=1, inplace=True)
    except FileNotFoundError:
        print("本地文件不存在，尝试从接口获取数据...")
        fund4df = THS_BD(','.join(fundcode4list),'ths_nb_mv_to_bond_invest_mv_fund;ths_zcxjrzszzzqtzszb_fund;ths_cbb_to_bond_invest_mv_fund',QDate+';'+QDate+';'+QDate).data
        fund4df.to_csv("input/BondFundData/Bond/Qbondtype" + QDate + ".csv")
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
        fund4df = pd.read_csv("input/BondFundData/Bond/HYBond" + HYDate + ".csv", dtype={'p00483_f002': str})
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
        NetValue_long = THS_HQ(','.join(fundcode4list[n * frequency::]), 'accumulatedNAV', 'CPS:3', date1, date2).data
        for j in range(n):
            df1 = THS_HQ(','.join(fundcode4list[j * frequency:(j + 1) * frequency]), 'accumulatedNAV', 'CPS:3', date1,
                         date2).data
            NetValue_long = pd.concat([NetValue_long, df1])

        NetValue = NetValue_long.pivot(index='time', columns='thscode', values='accumulatedNAV')
        NetValue.to_csv("input/BondFundData/NetValue/HYNetValue" + StartDate + '-' + EndDate + ".csv")
        NetValue = pd.read_csv("input/BondFundData/NetValue/HYNetValue" + StartDate + '-' + EndDate + ".csv")
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
        index4df = pd.read_csv("input/Index/HY" + onecode4char + "/HY" + StartDate + '-' + EndDate + ".csv")
        index4df.drop('Unnamed: 0', axis=1, inplace=True)
        # index4df.set_index('time', inplace=True)
    except FileNotFoundError:
        print("本地文件不存在，尝试从接口获取数据...")
        date1 = exchangedate1(StartDate)
        date2 = exchangedate1(EndDate)
        index4df = THS_HQ(onecode4char, 'close', 'CPS:3', date1, date2).data
        index4df.to_csv("input/Index/HY" + onecode4char + "/HY" + StartDate + '-' + EndDate + ".csv")
        index4df = pd.read_csv("input/Index/HY" + onecode4char + "/HY" + StartDate + '-' + EndDate + ".csv")
        # index4df.set_index('time', inplace=True)
    return index4df

# -----------------------------------------------获取股票相关数据-----------------------------------------------
def GetstockindustryData(HYDate, apikey):
    """
    获取全市场股票的行业数据
    :param HYDate:
    :param apikey:
    :return:
    """
    thsLogin = THS_iFinDLogin(apikey[0], apikey[1])
    try:
        aStockIndDF = pd.read_csv("input/StockData/Industry/HYindustry" + HYDate + ".csv")
        aStockIndDF.drop('Unnamed: 0', axis=1, inplace=True)
    except FileNotFoundError:
        # 获取某一时间所有A股股票代码
        allStock = THS_DR('p03291', 'date=' + HYDate + ';blockname=001005010;iv_type=allcontract', 'p03291_f002:Y',
                          'format:dataframe').data
        stockcode4list = df2list(allStock.iloc[:, [0]])

        print("本地文件不存在，尝试从接口获取数据...")
        frequency = 700  # 分批抓取
        n = int(len(stockcode4list) / frequency)

        # 中信一级行业
        aStockIndDF = THS_BD(stockcode4list[n * frequency::], 'ths_the_citic_industry_stock', '100,' + HYDate).data
        for i in range(n):
            df1 = THS_BD(stockcode4list[i * frequency:(i + 1) * frequency], 'ths_the_citic_industry_stock',
                         '100,' + HYDate).data
            aStockIndDF = pd.concat([aStockIndDF, df1])
        aStockIndDF.rename(columns={'ths_the_citic_industry_stock': 'firstInd'}, inplace=True)

        # 中信三级行业
        aStockIndDF1 = THS_BD(stockcode4list[n * frequency::], 'ths_the_citic_industry_stock', '102,' + HYDate).data
        for i in range(n):
            df2 = THS_BD(stockcode4list[i * frequency:(i + 1) * frequency], 'ths_the_citic_industry_stock',
                         '102,' + HYDate).data
            aStockIndDF1 = pd.concat([aStockIndDF1, df2])
        aStockIndDF1.rename(columns={'ths_the_citic_industry_stock': 'thirdInd'}, inplace=True)

        aStockIndDF = pd.concat([aStockIndDF, aStockIndDF1['thirdInd']], axis=1)
        aStockIndDF.to_csv("input/StockData/Industry/HYindustry" + HYDate + ".csv")
    return aStockIndDF

def GetstockstyleData(HYDate, apikey):
    """
    获取全市场股票的基本数据，用于晨星九宫格计算
    :param HYDate:
    :param apikey:
    :return:
    """
    thsLogin = THS_iFinDLogin(apikey[0], apikey[1])
    try:
        aStockInfoDF = pd.read_csv("input/StockFundData/Style/HYstyle" + HYDate + ".csv")
        aStockInfoDF.drop('Unnamed: 0', axis=1, inplace=True)
    except FileNotFoundError:
        print("本地文件不存在，尝试从接口获取数据...")
        # 获取某一时间所有A股股票
        allStock = THS_DR('p03291', 'date=' + HYDate + ';blockname=001005010;iv_type=allcontract','p03291_f002:Y','format:dataframe').data
        stockcode4list = df2list(allStock.iloc[:, [0]])
        frequency = 700
        n = int(len(stockcode4list) / frequency)

        # 末期截面基础数据
        aStockInfoDF = THS_BD(stockcode4list[n * frequency::],
                              'ths_market_value_stock;ths_pb_latest_stock;ths_pe_ttm_stock;ths_ps_ttm_stock'
                              ';ths_sq_np_yoy_stock;ths_revenue_yoy_sq_stock;ths_op_yoy_sq_stock'
                              ';ths_the_citic_industry_stock',
                              exchangedate1(HYDate) + ';' + exchangedate1(HYDate) + ',100;' + exchangedate1(HYDate) + ',100;' + exchangedate1(HYDate) + ',100;' + exchangedate1(HYDate) + ';' + exchangedate1(HYDate) + ';' + exchangedate1(HYDate) + ';100,' + HYDate).data
        for i in range(n):
            df1 = THS_BD(stockcode4list[i * frequency:(i + 1) * frequency],
                         'ths_market_value_stock;ths_pb_latest_stock;ths_pe_ttm_stock;ths_ps_ttm_stock'
                         ';ths_sq_np_yoy_stock;ths_revenue_yoy_sq_stock;ths_op_yoy_sq_stock'
                         ';ths_the_citic_industry_stock',
                         exchangedate1(HYDate) + ';' + exchangedate1(HYDate) + ',100;' + exchangedate1(HYDate) + ',100;' + exchangedate1(HYDate) + ',100;' + exchangedate1(HYDate) + ';' + exchangedate1(HYDate) + ';' + exchangedate1(HYDate) + ';100,' + HYDate).data
            aStockInfoDF = pd.concat([aStockInfoDF, df1])
        aStockInfoDF.to_csv("input/StockFundData/Style/HYstyle" + HYDate + ".csv")
        aStockInfoDF = pd.read_csv("input/StockFundData/Style/HYstyle" + HYDate + ".csv")
        aStockInfoDF.drop('Unnamed: 0', axis=1, inplace=True)
    return aStockInfoDF

def GetindindexData(beginDate,endDate,apikey):
    """
    获取中信产业指数
    :param beginDate:
    :param endDate:
    :param apikey:
    :return:
    """
    thsLogin = THS_iFinDLogin(apikey[0], apikey[1])
    try:
        ind4df = pd.read_csv("input/Index/Ind/Ind" + beginDate+"-"+ endDate + ".csv")
        ind4df.drop('Unnamed: 0', axis=1, inplace=True)
    except FileNotFoundError:
        print("本地文件不存在，尝试从接口获取数据...")
        ind4df = THS_HQ('CI005925.CI,CI005926.CI,CI005928.CI,CI005929.CI,CI005930.CI,CI005931.CI', 'close', 'CPS:3',
                        exchangedate1(beginDate), exchangedate1(endDate)).data
        ind4df.to_csv("input/Index/Ind/Ind" + beginDate+"-"+ endDate + ".csv")
    ind4df = ind4df.pivot(index='time', columns='thscode', values='close')
    return ind4df

# -----------------------------------------------获取股票基金相关数据-----------------------------------------------
def GetsfundbasicData(QDate, apikey):
    """
    获取股票基金的全市场数据
    :param QDate:
    :param apikey:
    :return:
    """
    thsLogin = THS_iFinDLogin(apikey[0], apikey[1])
    try:
        AllFundDF = pd.read_csv("input/StockFundData/Basic/Qbasic" + QDate + ".csv")
        AllFundDF.drop('Unnamed: 0', axis=1, inplace=True)
    except FileNotFoundError:
        print("本地文件不存在，尝试从接口获取数据...")
        # 获取基金代码
        # 上市股票型开放式基金
        IPOStockFund = THS_DR('p03291', 'date=' + QDate + ';blockname=051001022001;iv_type=allcontract',
                              'p03291_f002:Y,p03291_f003:Y', 'format:dataframe').data.iloc[:, [0]].values.tolist()
        IPOStockFund1 = [item for sublist in IPOStockFund for item in sublist]
        # 非上市股票型开放式基金
        NoIPOStockFund = THS_DR('p03291', 'date=' + QDate + ';blockname=051001022002;iv_type=allcontract',
                                'p03291_f002:Y,p03291_f003:Y', 'format:dataframe').data.iloc[:, [0]].values.tolist()
        NoIPOStockFund1 = [item for sublist in NoIPOStockFund for item in sublist]
        # 上市混合型开放式基金
        MixedIPOFund = THS_DR('p03291', 'date=' + QDate + ';blockname=051001024001;iv_type=allcontract',
                              'p03291_f002:Y,p03291_f003:Y', 'format:dataframe').data.iloc[:, [0]].values.tolist()
        MixedIPOFund1 = [item for sublist in MixedIPOFund for item in sublist]
        # 非上市混合型开放式基金
        NoMixedFund = THS_DR('p03291', 'date=' + QDate + ';blockname=051001024002;iv_type=allcontract',
                             'p03291_f002:Y,p03291_f003:Y', 'format:dataframe').data.iloc[:, [0]].values.tolist()
        NoMixedFund1 = [item for sublist in NoMixedFund for item in sublist]

        # 获取全部数据并保存为csv文件
        AllFund = IPOStockFund1 + NoIPOStockFund1 + MixedIPOFund1 + NoMixedFund1
        n = int(len(AllFund) / 1000)
        # 末期截面基础数据
        AllFundDF = THS_BD(AllFund[n * 1000::],
                           'ths_fund_short_name_fund;ths_fund_manager_current_fund;ths_fund_manager_his_fund'
                           ';ths_isindexfund_fund;ths_invest_type_first_classi_fund;ths_invest_type_second_classi_fund'
                           ';ths_fund_scale_fund;ths_found_years_fund;ths_org_investor_held_ratio_fund'
                           ';ths_stock_mv_to_fanv_fund',
                           ';;;;;;' + exchangedate1(QDate) + ';' + exchangedate1(QDate) + ';' + exchangedate1(
                               QDate) + ';' + QDate).data
        for i in range(n):
            df1 = THS_BD(AllFund[i * 1000:(i + 1) * 1000],
                         'ths_fund_short_name_fund;ths_fund_manager_current_fund;ths_fund_manager_his_fund'
                         ';ths_isindexfund_fund;ths_invest_type_first_classi_fund;ths_invest_type_second_classi_fund'
                         ';ths_fund_scale_fund;ths_found_years_fund;ths_org_investor_held_ratio_fund'
                         ';ths_stock_mv_to_fanv_fund',
                         ';;;;;;' + exchangedate1(QDate) + ';' + exchangedate1(QDate) + ';' + exchangedate1(
                             QDate) + ';' + QDate).data
            AllFundDF = pd.concat([AllFundDF, df1])
        AllFundDF.to_csv("input/StockFundData/Basic/Qbasic" + QDate + ".csv")

    return AllFundDF

# 获取各期数据代码的可以再优化一下
def GetsfundscaleData(fundcode4list, repDateQ, apikey):
    """
    获取筛选后从2018年至今各季度股票基金的基金规模
    :param QDate:
    :param apikey:
    :return:
    """
    thsLogin = THS_iFinDLogin(apikey[0], apikey[1])
    try:
        ScaleDF = pd.read_csv("input/StockFundData/Scale/Qscale" + repDateQ[-1] + ".csv")
        ScaleDF.drop('Unnamed: 0', axis=1, inplace=True)
    except FileNotFoundError:
        print("本地文件不存在，尝试从接口获取数据...")
        len_date = len(repDateQ)
        for i in range(len_date):
            list2 = THS_BD(fundcode4list, 'ths_fund_scale_fund', repDateQ[i]).data
            if i == 0:
                ScaleDF = list2
            else:
                list2.columns = ['code', i]
                ScaleDF = pd.concat([ScaleDF, list2[i]], axis=1)

        ScaleDF['Mean'] = ScaleDF.iloc[:, 1:].mean(axis=1)
        ScaleDF.to_csv("input/StockFundData/Scale/Qscale" + repDateQ[-1] + ".csv")
    return ScaleDF


def GetsfundsratioData(fundcode4list, repDateQ, apikey):
    """
    获取筛选后从2018年至今各季度股票基金的权益仓位
    :param fundcode4list:
    :param repDateQ:
    :param apikey:
    :return:
    """
    thsLogin = THS_iFinDLogin(apikey[0], apikey[1])
    try:
        StockRatioDF = pd.read_csv("input/StockFundData/Stockratio/Allratio" + repDateQ[-1] + ".csv")
        StockRatioDF.drop('Unnamed: 0', axis=1, inplace=True)
    except FileNotFoundError:
        print("本地文件不存在，尝试从接口获取数据...")
        len_date = len(repDateQ)
        for i in range(len_date):
            df1 = THS_BD(fundcode4list, 'ths_stock_mv_to_fanv_fund', repDateQ[i]).data
            if i == 0:
                StockRatioDF = df1
            else:
                df1.columns = ['code', i]
                StockRatioDF = pd.concat([StockRatioDF, df1[i]], axis=1)
        StockRatioDF['Mean'] = StockRatioDF.iloc[:, 1:].mean(axis=1)
        StockRatioDF.to_csv("input/StockFundData/Stockratio/Allratio" + repDateQ[-1] + ".csv")

    return StockRatioDF

def GetsfundastockData(fundcode4list, HYDate, apikey):
    """
    获取股票基金的股票持仓具体数据
    :param fundcode4list:
    :param HYDate:
    :param apikey:
    :return:
    """
    thsLogin = THS_iFinDLogin(apikey[0], apikey[1])
    try:
        FundRatioDF = pd.read_csv("input/StockFundData/Ratio/HYratio" + HYDate + ".csv")
        FundRatioDF.drop('Unnamed: 0', axis=1, inplace=True)
    except FileNotFoundError:
        print("本地文件不存在，尝试从接口获取数据...")
        # 获取全部基金持仓数据
        FundRatioDF = THS_DR('p00475', 'bgqlb=' + HYDate + ';jjlb=' + ','.join(fundcode4list) + ';tzlx=0',
                             'jydm:Y,jydm_mc:Y,p00475_f001:Y,p00475_f002:Y,p00475_f009:Y', 'format:dataframe').data
        FundRatioDF.to_csv("input/StockFundData/Ratio/HYratio" + HYDate + ".csv")

    return FundRatioDF

def Getsfund10stockData(fundcode4list, QDate, apikey):
    """
    获取股票基金的前十大持仓
    :param fundcode4list:
    :param QDate:
    :param apikey:
    :return:
    """
    thsLogin = THS_iFinDLogin(apikey[0], apikey[1])
    try:
        HDF = pd.read_csv("input/StockFundData/Top10stock/Qindependent" + QDate + ".csv")
        HDF.drop('Unnamed: 0', axis=1, inplace=True)
    except FileNotFoundError:
        print("本地文件不存在，尝试从接口获取数据...")
        for i in range(10):
            # 前十大持仓
            df1 = THS_BD(fundcode4list,'ths_fund_num_of_heavily_held_sec_fund;ths_top_sec_held_num_fund',QDate + ',' + str(i + 1) + ';' + QDate + ',' + str(i + 1)).data
            df1.rename(columns={'ths_fund_num_of_heavily_held_sec_fund': 'x' + str(i + 1),'ths_top_sec_held_num_fund': 'ww' + str(i + 1)}, inplace=True)
            if i == 0:
                HDF = df1
            else:
                HDF = pd.merge(HDF, df1, on='thscode', how='left')
        HDF.to_csv("input/StockFundData/Top10stock/Qindependent" + QDate + ".csv")
    return HDF

def Getsfund10sumstockData(fundcode4list, QDate, apikey):
    """
    获取股票基金的前十大持仓总和
    :param fundcode4list:
    :param QDate:
    :param apikey:
    :return:
    """
    thsLogin = THS_iFinDLogin(apikey[0], apikey[1])
    try:
        HDF = pd.read_csv("input/StockFundData/Top10sumstock/Qtop10" + QDate + ".csv")
        HDF.drop('Unnamed: 0', axis=1, inplace=True)
    except FileNotFoundError:
        print("本地文件不存在，尝试从接口获取数据...")
        # 前十大持仓总和
        HDF = THS_BD(fundcode4list,'ths_top_n_top_stock_mv_to_si_mv_fund',QDate+',10').data
        HDF.to_csv("input/StockFundData/Top10sumstock/Qtop10" + QDate + ".csv")
    return HDF

def GetsfundnetvalueData(fundcode4list, StartDate, EndDate, apikey):
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
        NetValue = pd.read_csv("input/StockFundData/NetValue/HYNetValue" + StartDate + '-' + EndDate + ".csv")
    except FileNotFoundError:
        # 一段一段获取数据
        print("本地文件不存在，尝试从接口获取数据...")
        date1 = exchangedate1(StartDate)
        date2 = exchangedate1(EndDate)

        frequency = 300
        n = int(len(fundcode4list) / frequency)
        # 末期截面基础数据
        NetValue_long = THS_HQ(','.join(fundcode4list[n * frequency::]), 'accumulatedNAV', 'CPS:3', date1, date2).data
        for j in range(n):
            df1 = THS_HQ(','.join(fundcode4list[j * frequency:(j + 1) * frequency]), 'accumulatedNAV', 'CPS:3', date1, date2).data
            NetValue_long = pd.concat([NetValue_long, df1])
        NetValue = NetValue_long.pivot(index='time', columns='thscode', values='accumulatedNAV')
        NetValue.to_csv("input/StockFundData/NetValue/HYNetValue" + StartDate + '-' + EndDate + ".csv")
        NetValue = pd.read_csv("input/StockFundData/NetValue/HYNetValue" + StartDate + '-' + EndDate + ".csv")
    return NetValue