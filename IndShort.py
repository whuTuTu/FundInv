# -*- coding: UTF-8 -*-
"""
@Project ：FundInv 
@File    ：IndShort.py
@IDE     ：PyCharm 
@Author  ：tutu
@Date    ：2023-08-18 10:53
本文件用于给基金打上行业主题标签。股票采用中信行业分类。基金采用半年报和年报全部持仓数据，每半年跑一次。
要用基金的全部持仓
该文件为行业短期标签
"""
# 载入包
from iFinDPy import *  # 同花顺API接口
import pandas as pd
import warnings

warnings.filterwarnings(action='ignore')  # 导入warnings模块，并指定忽略代码运行中的警告信息


def shortInd(lastYearDate, apikey):
    """
    基金池短期的行业主题标签
    :param lastYearDate: 年报或者半年报日期例如20220630或者20221231
    :param apikey: list，["tfzq1556", "752862"]
    :return: 无返回，输出从csv文件
    """

    # 接入同花顺API接口
    thsLogin = THS_iFinDLogin(apikey[0], apikey[1])

    # 获取某一时间所有A股股票
    allStock = THS_DR('p03291', 'date=' + lastYearDate + ';blockname=001005010;iv_type=allcontract', 'p03291_f002:Y',
                      'format:dataframe').data.iloc[:, [0]].values.tolist()
    allStock1 = [item for sublist in allStock for item in sublist]
    # print("A股市场股票总数为:{}".format(len(allStock1)))

    # 尝试从本地文件读取数据
    try:
        aStockIndDF = pd.read_csv("input/aStockIndDF" + lastYearDate + ".csv")
        aStockIndDF.drop('Unnamed: 0', axis=1, inplace=True)
    except FileNotFoundError:
        print("本地文件不存在，尝试从接口获取数据...")
        frequency = 700  # 分批抓取
        n = int(len(allStock1) / frequency)

        # 中信一级行业
        aStockIndDF = THS_BD(allStock1[n * frequency::], 'ths_the_citic_industry_stock', '100,' + lastYearDate).data
        for i in range(n):
            df1 = THS_BD(allStock1[i * frequency:(i + 1) * frequency], 'ths_the_citic_industry_stock',
                         '100,' + lastYearDate).data
            aStockIndDF = pd.concat([aStockIndDF, df1])
        aStockIndDF.rename(columns={'ths_the_citic_industry_stock': 'firstInd'}, inplace=True)

        # 中信三级行业
        aStockIndDF1 = THS_BD(allStock1[n * frequency::], 'ths_the_citic_industry_stock', '102,' + lastYearDate).data
        for i in range(n):
            df2 = THS_BD(allStock1[i * frequency:(i + 1) * frequency], 'ths_the_citic_industry_stock',
                         '102,' + lastYearDate).data
            aStockIndDF1 = pd.concat([aStockIndDF1, df2])
        aStockIndDF1.rename(columns={'ths_the_citic_industry_stock': 'thirdInd'}, inplace=True)

        aStockIndDF = pd.concat([aStockIndDF, aStockIndDF1['thirdInd']], axis=1)
        aStockIndDF.to_csv("input/aStockIndDF" + lastYearDate + ".csv")

    # 一级分类
    xiaofei = ['食品饮料', '商贸零售', '消费者服务', '家电', '纺织服', '农林牧渔']
    yiyao = ['医药']
    zhouqi = ['石油石化', '煤炭', '有色金属', '钢铁', '基础化工', '建筑', '建材', '轻工制造']
    zhizhao = ['机械', '电力设备及新能源', '国防军工', '汽车']
    TMT = ['通信', '计算机', '传媒', '电子']
    JRDC = ['银行', '非银行金融', '综合金融', '房地产']
    # others = ['交通运输、电力及公用事业、综合']

    # 三级分类特例
    alist = ['航运', '航空', '港口']
    clist = ['乘用车Ⅲ', '摩托车及其他', '汽车消费及服务Ⅲ']
    dlist = ['家具', '文娱轻工', '其他家居']

    # 分类
    for index, row in aStockIndDF.iterrows():
        if row['firstInd'] in xiaofei:
            aStockIndDF.loc[index, 'IND'] = '消费'
        elif row['firstInd'] in yiyao:
            aStockIndDF.loc[index, 'IND'] = '医药'
        elif row['firstInd'] in zhouqi:
            if row['firstInd'] == '轻工制造' and row['thirdInd'] in dlist:
                aStockIndDF.loc[index, 'IND'] = '消费'
            else:
                aStockIndDF.loc[index, 'IND'] = '周期'
        elif row['firstInd'] in zhizhao:
            if row['firstInd'] == '汽车' and row['thirdInd'] in clist:
                aStockIndDF.loc[index, 'IND'] = '消费'
            else:
                aStockIndDF.loc[index, 'IND'] = '制造'
        elif row['firstInd'] in TMT:
            aStockIndDF.loc[index, 'IND'] = 'TMT'
        elif row['firstInd'] in JRDC:
            aStockIndDF.loc[index, 'IND'] = '金融地产'
        elif row['firstInd'] == '交通运输' and row['thirdInd'] in alist:
            aStockIndDF.loc[index, 'IND'] = '周期'
        else:
            aStockIndDF.loc[index, 'IND'] = '其他'

    # 对我的基金池进行行业主题分类
    MyFundDF = pd.read_csv("output/MyFundDF.csv")
    MyFundDF.drop('Unnamed: 0', axis=1, inplace=True)
    MyFundList = MyFundDF.iloc[:, [0]].values.tolist()
    MyFundList = [item for sublist in MyFundList for item in sublist]
    MyFundChar = ','.join(MyFundList)

    try:
        FundRatioDF = pd.read_csv("input/FundRatioDF" + lastYearDate + ".csv")
        FundRatioDF.drop('Unnamed: 0', axis=1, inplace=True)
    except FileNotFoundError:
        print("本地文件不存在，尝试从接口获取数据...")
        # 获取全部基金持仓数据
        FundRatioDF = THS_DR('p00475', 'bgqlb=' + lastYearDate + ';jjlb=' + MyFundChar + ';tzlx=0',
                             'jydm:Y,jydm_mc:Y,p00475_f001:Y,p00475_f002:Y,p00475_f009:Y', 'format:dataframe').data
        FundRatioDF.to_csv("input/FundRatioDF" + lastYearDate + ".csv")

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

    print('{}行业标签成功匹配的基金比例为：{}/{}'.format(lastYearDate,len(result), len(MyFundList)))
    result.rename(columns={'jydm': 'thscode'}, inplace=True)
    return result[['thscode','INDtype']]
