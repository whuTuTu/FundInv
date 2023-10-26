# -*- coding: UTF-8 -*-
"""
@Project ：FundInv 
@File    ：StockfundFirstfilter.py
@IDE     ：PyCharm
@Author  ：tutu
@Date    ：2023-08-18 9:32
第一次筛选，此文件包括末期截面数据的初筛（包括成立年限，管理人，ACE，是否为指数型基金）
和利用时间序列数据（每期规模，每期权益仓位）
数据量较大，谨慎使用
输入截至交易日，会自动找到上一个季度报告期
"""
# 载入包
from iFinDPy import *  # 同花顺API接口
import pandas as pd
import os
import warnings
from InvokingFunction.GetData import GetsfundbasicData, GetsfundscaleData, GetsfundsratioData
from InvokingFunction.GetGFunction import getQtime4liet, exchangedate1, df2list
warnings.filterwarnings(action='ignore')  # 导入warnings模块，并指定忽略代码运行中的警告信息
# 更改相对路径
path = "D:\TFCode\FundInv"
os.chdir(path)

def StockFirstFilter(endDate, apikey):
    """
    进行股票基金的第一次筛选，得到初筛池
    :param endDate: 最终交易日
    :param apikey: list，["tfzq1556", "752862"]
    :return:list，返回基金代码，输出csv文件
    """
    # 接入同花顺API接口
    thsLogin = THS_iFinDLogin(apikey[0], apikey[1])

    # ------------------------------------------生成相关时间变量---------------------------------------------------
    beginDate = "20180101"
    repDateQ = getQtime4liet(beginDate, endDate)
    lastRepDate = repDateQ[-1]
    # ------------------------------------------下面为代码--------------------------------------------------------
    AllFundDF = GetsfundbasicData(lastRepDate, apikey)
    print('基金池总个数为：{}'.format(len(AllFundDF)))

    # 成立年限>=3
    filterFundDF = AllFundDF[AllFundDF['ths_found_years_fund'] >= 3]
    print('根据年限筛选后基金池总个数为：{}'.format(len(filterFundDF)))

    # 至少从2020年开始管理
    date_lists = filterFundDF['ths_fund_manager_his_fund'].str.findall(r'(\d{8})-至今')
    filterFundDF['sinceyear'] = date_lists.apply(lambda x: sorted(x)[0])
    filterFundDF['sinceyear'] = pd.to_numeric(filterFundDF['sinceyear'], errors='coerce')
    filterFundDF = filterFundDF[filterFundDF['sinceyear'] <= 20200101]
    print('根据管理人筛选后基金池总个数为：{}'.format(len(filterFundDF)))

    # 不是指数型基金
    filterFundDF = filterFundDF[filterFundDF['ths_isindexfund_fund'] != "是"]
    print('根据主被动筛选后基金池总个数为：{}'.format(len(filterFundDF)))

    # 只保留A份额的基金
    filterFundDF['ACEtype'] = filterFundDF['ths_fund_short_name_fund'].str.findall(r'(A|C|E)').apply(''.join)
    filterFundDF = filterFundDF[filterFundDF['ACEtype'].str.contains('A') | ~filterFundDF['ACEtype'].str.contains('[ACE]')]
    print('根据ACE筛选后基金池总个数为：{}'.format(len(filterFundDF)))

    # 基金规模时间序列数据进行筛选
    filterFundcode4list = df2list(filterFundDF.iloc[:, [0]])
    Scale4df = GetsfundscaleData(filterFundcode4list, repDateQ, apikey)  # 获取各期规模数据
    filterFundDF = Scale4df[(Scale4df.iloc[:, 1:-1] >= 50000000).all(axis=1)]
    print('基金规模筛选出来的基金池个数为：{}'.format(len(filterFundDF)))  # 第二次筛选出来的基金池

    # 权益仓位时间序列数据进行筛选
    StockRatioDF = GetsfundsratioData(filterFundcode4list, repDateQ, apikey)
    filterFundDF = StockRatioDF[(StockRatioDF.iloc[:, 1:-1] >= 60).all(axis=1) & (StockRatioDF.iloc[:, -1] >= 70)]  # 每个节点大于60，均值大于70
    print('权益仓位筛选出来的基金池个数为：{}'.format(len(filterFundDF)))

    # 查看筛选出基金的基本情况
    filterFundcode4list = df2list(filterFundDF.iloc[:, [0]])
    BasicDF = pd.read_csv("input/StockFundData/Basic/Qbasic" + lastRepDate + ".csv")
    BasicDF.drop('Unnamed: 0', axis=1, inplace=True)
    MyFundDF = BasicDF[BasicDF['thscode'].isin(filterFundcode4list)]
    MyFundDF.to_csv("output/StockFund/stockfund_filter.csv")
    return MyFundDF
