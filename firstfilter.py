# -*- coding: UTF-8 -*-
"""
@Project ：FundInv 
@File    ：firstfilter.py
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
import warnings

warnings.filterwarnings(action='ignore')  # 导入warnings模块，并指定忽略代码运行中的警告信息


def FirstFilter(endDate, apikey):
    """
    进行基金的第一次筛选，得到初筛池
    :param endDate: 最终交易日
    :param apikey: list，["tfzq1556", "752862"]
    :return:list，返回基金代码，输出csv文件
    """
    # 接入同花顺API接口
    thsLogin = THS_iFinDLogin(apikey[0], apikey[1])

    # ------------------------------------------生成相关时间变量--------------------------------------------------------
    beginDate = "20180101"
    endDate1 = endDate[0:4] + '-' + endDate[4:6] + '-' + endDate[6::]
    beginyear = beginDate[0:4]
    endyear = endDate[0:4]
    monthday = ['0331', '0630', '0930', '1231']
    aRepDate = [str(i) + j for i in range(int(beginyear), int(endyear) + 1) for j in monthday]
    repDate = []
    for i in aRepDate:
        if endDate >= i >= beginDate:
            repDate.append(i)
        else:
            continue
    lastRepDate = repDate[-1]
    lastRepDate1 = lastRepDate[0:4] + '-' + lastRepDate[4:6] + '-' + lastRepDate[6::]

    # ------------------------------------------下面为代码--------------------------------------------------------
    # 尝试从本地文件读取数据
    try:
        AllFundDF = pd.read_csv("input/BasicDF" + lastRepDate + ".csv")
        AllFundDF.drop('Unnamed: 0', axis=1, inplace=True)
    except FileNotFoundError:
        print("本地文件不存在，尝试从接口获取数据...")
        # 获取基金代码
        # 上市股票型开放式基金
        IPOStockFund = THS_DR('p03291', 'date=' + endDate + ';blockname=051001022001;iv_type=allcontract',
                              'p03291_f002:Y,p03291_f003:Y', 'format:dataframe').data.iloc[:, [0]].values.tolist()
        IPOStockFund1 = [item for sublist in IPOStockFund for item in sublist]
        # 非上市股票型开放式基金
        NoIPOStockFund = THS_DR('p03291', 'date=' + endDate + ';blockname=051001022002;iv_type=allcontract',
                                'p03291_f002:Y,p03291_f003:Y', 'format:dataframe').data.iloc[:, [0]].values.tolist()
        NoIPOStockFund1 = [item for sublist in NoIPOStockFund for item in sublist]
        # 上市混合型开放式基金
        MixedIPOFund = THS_DR('p03291', 'date=' + endDate + ';blockname=051001024001;iv_type=allcontract',
                              'p03291_f002:Y,p03291_f003:Y', 'format:dataframe').data.iloc[:, [0]].values.tolist()
        MixedIPOFund1 = [item for sublist in MixedIPOFund for item in sublist]
        # 非上市混合型开放式基金
        NoMixedFund = THS_DR('p03291', 'date=' + endDate + ';blockname=051001024002;iv_type=allcontract',
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
                           ';;;;;;' + endDate1 + ';' + endDate1 + ';' + lastRepDate1 + ';' + lastRepDate).data
        for i in range(n):
            df1 = THS_BD(AllFund[i * 1000:(i + 1) * 1000],
                         'ths_fund_short_name_fund;ths_fund_manager_current_fund;ths_fund_manager_his_fund'
                         ';ths_isindexfund_fund;ths_invest_type_first_classi_fund;ths_invest_type_second_classi_fund'
                         ';ths_fund_scale_fund;ths_found_years_fund;ths_org_investor_held_ratio_fund'
                         ';ths_stock_mv_to_fanv_fund',
                         ';;;;;;' + endDate1 + ';' + endDate1 + ';' + lastRepDate1 + ';' + lastRepDate).data
            AllFundDF = pd.concat([AllFundDF, df1])
        AllFundDF.to_csv("input/BasicDF" + lastRepDate + ".csv")

    # 开始进行基金的筛选
    print('基金池总个数为：{}'.format(len(AllFundDF)))
    filterFundDF = AllFundDF[AllFundDF['ths_found_years_fund'] >= 3]  # 成立年限>=3
    print('根据年限筛选后基金池总个数为：{}'.format(len(filterFundDF)))

    date_lists = filterFundDF['ths_fund_manager_his_fund'].str.findall(r'(\d{8})-至今')
    filterFundDF['sinceyear'] = date_lists.apply(lambda x: sorted(x)[0])
    filterFundDF['sinceyear'] = pd.to_numeric(filterFundDF['sinceyear'], errors='coerce')
    filterFundDF = filterFundDF[filterFundDF['sinceyear'] <= 20200101]  # 至少从2020年开始管理
    print('根据管理人筛选后基金池总个数为：{}'.format(len(filterFundDF)))

    filterFundDF = filterFundDF[filterFundDF['ths_isindexfund_fund'] != "是"]  # 不是指数型基金
    print('根据主被动筛选后基金池总个数为：{}'.format(len(filterFundDF)))

    filterFundDF['ACEtype'] = filterFundDF['ths_fund_short_name_fund'].str.findall(r'(A|C|E)').apply(''.join)
    filterFundDF = filterFundDF[filterFundDF['ACEtype'].str.contains('A') |
                                ~filterFundDF['ACEtype'].str.contains('[ACE]')]  # 只保留A份额的基金
    print('根据ACE筛选后基金池总个数为：{}'.format(len(filterFundDF)))

    Allfund2 = filterFundDF.iloc[:, [0]].values.tolist()
    Allfund2 = [item for sublist in Allfund2 for item in sublist]

    # 基金规模时间序列数据进行筛选
    try:
        ScaleDF = pd.read_csv("input/ScaleDF" + lastRepDate + ".csv")
        ScaleDF.drop('Unnamed: 0', axis=1, inplace=True)
    except FileNotFoundError:
        print("本地文件不存在，尝试从接口获取数据...")
        ScaleDF = THS_BD(Allfund2, 'ths_fund_scale_fund', repDate[0]).data['thscode']
        for i in repDate:
            list2 = THS_BD(Allfund2, 'ths_fund_scale_fund', i).data
            list2.columns = ['code', i]
            ScaleDF = pd.concat([ScaleDF, list2[i]], axis=1)
        ScaleDF['Mean'] = ScaleDF.iloc[:, 1:].mean(axis=1)
        ScaleDF.to_csv("input/ScaleDF" + lastRepDate + ".csv")

    filterFundDF = ScaleDF[(ScaleDF.iloc[:, 1:-1] >= 50000000).all(axis=1)]
    Allfund3 = filterFundDF.iloc[:, [0]].values.tolist()
    Allfund3 = [item for sublist in Allfund3 for item in sublist]
    print('基金规模筛选出来的基金池个数为：{}'.format(len(Allfund3)))  # 第二次筛选出来的基金池

    # 权益仓位时间序列数据进行筛选
    try:
        StockRatioDF = pd.read_csv("input/StockRatioDF" + lastRepDate + ".csv")
        StockRatioDF.drop('Unnamed: 0', axis=1, inplace=True)
    except FileNotFoundError:
        print("本地文件不存在，尝试从接口获取数据...")
        StockRatioDF = THS_BD(Allfund3, 'ths_stock_mv_to_fanv_fund', repDate[0]).data['thscode']
        for i in repDate:
            list3 = THS_BD(Allfund3, 'ths_stock_mv_to_fanv_fund', i).data
            list3.columns = ['code', i]
            StockRatioDF = pd.concat([StockRatioDF, list3[i]], axis=1)
        StockRatioDF['Mean'] = StockRatioDF.iloc[:, 1:].mean(axis=1)
        StockRatioDF.to_csv("input/StockRatioDF" + lastRepDate + ".csv")

    filterFundDF = StockRatioDF[
        (StockRatioDF.iloc[:, 1:-1] >= 60).all(axis=1) & (StockRatioDF.iloc[:, -1] >= 70)]  # 每个节点大于60，均值大于70
    Allfund4 = filterFundDF.iloc[:, [0]].values.tolist()
    Allfund4 = [item for sublist in Allfund4 for item in sublist]
    print('权益仓位筛选出来的基金池个数为：{}'.format(len(Allfund4)))

    # 查看筛选出基金的基本情况
    BasicDF = pd.read_csv("input/BasicDF" + lastRepDate + ".csv")
    BasicDF.drop('Unnamed: 0', axis=1, inplace=True)
    MyFundDF = BasicDF[BasicDF['thscode'].isin(Allfund4)]
    MyFundDF.to_csv("output/MyFundDF.csv")

    return MyFundDF[['thscode', 'ths_fund_short_name_fund', 'ths_fund_manager_current_fund']]
