# -*- coding: UTF-8 -*-
"""
@Project ：FundInv 
@File    ：StyleShort.py
@IDE     ：PyCharm
@Author  ：tutu
@Date    ：2023-08-22 11:31
本文件用于给基金打上风格标签。股票采用中信行业分类。数据要用基金的全部持仓
该文件为风格短期标签
"""

# 载入包
from iFinDPy import *  # 同花顺API接口
import pandas as pd
from MyFunction import *  # 同花顺API接口
import warnings
warnings.filterwarnings(action='ignore')  # 导入warnings模块，并指定忽略代码运行中的警告信息


def StyleShort(lastYearDate, apikey):
    """
    基金池短期的风格标签
    :param lastYearDate:季度报告期
    :param apikey: list，["tfzq1556", "752862"]
    :return: 无返回，输出从csv文件
    """
    # 接入同花顺API接口
    thsLogin = THS_iFinDLogin(apikey[0], apikey[1])
    lastYearDate1 = lastYearDate[0:4] + '-' + lastYearDate[4:6] + '-' + lastYearDate[6::]

    # 获取某一时间所有A股股票
    allStock = THS_DR('p03291', 'date=' + lastYearDate + ';blockname=001005010;iv_type=allcontract', 'p03291_f002:Y',
                      'format:dataframe').data.iloc[:, [0]].values.tolist()
    allStock1 = [item for sublist in allStock for item in sublist]

    # 尝试从本地文件读取数据
    try:
        aStockInfoDF = pd.read_csv("input/aStockInfoDF" + lastYearDate + ".csv")
        aStockInfoDF.drop('Unnamed: 0', axis=1, inplace=True)
    except FileNotFoundError:
        print("本地文件不存在，尝试从接口获取数据...")
        frequency = 700
        n = int(len(allStock1) / frequency)

        # 末期截面基础数据
        aStockInfoDF = THS_BD(allStock1[n * frequency::],
                              'ths_market_value_stock;ths_pb_latest_stock;ths_pe_ttm_stock;ths_ps_ttm_stock'
                              ';ths_sq_np_yoy_stock;ths_revenue_yoy_sq_stock;ths_op_yoy_sq_stock'
                              ';ths_the_citic_industry_stock',
                              lastYearDate1 + ';' + lastYearDate1 + ',100;' + lastYearDate1 + ',100;' + lastYearDate1 + ',100;' + lastYearDate1 + ';' + lastYearDate1 + ';' + lastYearDate1 + ';100,' + lastYearDate).data
        for i in range(n):
            df1 = THS_BD(allStock1[i * frequency:(i + 1) * frequency],
                         'ths_market_value_stock;ths_pb_latest_stock;ths_pe_ttm_stock;ths_ps_ttm_stock'
                         ';ths_sq_np_yoy_stock;ths_revenue_yoy_sq_stock;ths_op_yoy_sq_stock'
                         ';ths_the_citic_industry_stock',
                         lastYearDate1 + ';' + lastYearDate1 + ',100;' + lastYearDate1 + ',100;' + lastYearDate1 + ',100;' + lastYearDate1 + ';' + lastYearDate1 + ';' + lastYearDate1 + ';100,' + lastYearDate).data
            aStockInfoDF = pd.concat([aStockInfoDF, df1])
            # print("aStockInfoDF的长度{}".format(len(aStockInfoDF)))
        aStockInfoDF.to_csv("input/aStockInfoDF" + lastYearDate + ".csv")

    # 读取数据
    aStockInfoDF = pd.read_csv("input/aStockInfoDF" + lastYearDate + ".csv")
    aStockInfoDF.drop('Unnamed: 0', axis=1, inplace=True)

    missing_values_count = aStockInfoDF.isnull().sum(axis=1)
    rows_with_missing = missing_values_count[missing_values_count > 0]
    print("{}存在缺失值的行数为：{}".format(lastYearDate,len(rows_with_missing)))
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

    # 找出大中小盘的门限值
    # print("大盘的股票数量为：{}".format(len(StockInfoDF[StockInfoDF['Flag'] == 'Big'])))
    # print("中盘的股票数量为：{}".format(len(StockInfoDF[StockInfoDF['Flag'] == 'Mid'])))
    # print("小盘的股票数量为：{}".format(len(StockInfoDF[StockInfoDF['Flag'] == 'Small'])))
    StockInfoDF['LMT'] = StockInfoDF.loc[199,'ths_market_value_stock']
    StockInfoDF['MST'] = StockInfoDF.loc[499,'ths_market_value_stock']

    # 计算价值得分
    StockInfoDF['BP'] = 1 / StockInfoDF['ths_pb_latest_stock']
    StockInfoDF['EPTTM'] = 1 / StockInfoDF['ths_pe_ttm_stock']
    StockInfoDF['SPTTM'] = 1 / StockInfoDF['ths_ps_ttm_stock']

    StockInfoDF['BP1'] = StockInfoDF.groupby('Flag')['BP'].rank(method='first')
    StockInfoDF['EPTTM1'] = StockInfoDF.groupby('Flag')['EPTTM'].rank(method='first')
    StockInfoDF['SPTTM1'] = StockInfoDF.groupby('Flag')['SPTTM'].rank(method='first')
    weightOVS = [0.5, 0.25, 0.25]
    StockInfoDF['OVS'] = StockInfoDF['BP1'] * weightOVS[0] + StockInfoDF['EPTTM1'] * weightOVS[1] + StockInfoDF['SPTTM1'] * \
                         weightOVS[2]

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
    MyFundDF = pd.read_csv("output/MyFundDF.csv")
    MyFundDF.drop('Unnamed: 0', axis=1, inplace=True)
    MyFundList = MyFundDF.iloc[:, [0]].values.tolist()
    MyFundList = [item for sublist in MyFundList for item in sublist]
    # print("基金总数为：{}".format(len(MyFundList)))
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
    result.iloc[one_fifth:(2*one_fifth), result.columns.get_loc('Xstyle')] = '成长-均衡型'
    result.iloc[(one_fifth*3):(4*one_fifth), result.columns.get_loc('Xstyle')] = '均衡-价值型'
    result.iloc[-one_fifth:, result.columns.get_loc('Xstyle')] = '价值型'

    result['Ystyle'] = result.apply(style_divide2, axis=1)
    # result.to_csv("output/style" + lastYearDate + ".csv")
    print('{}风格标签成功匹配的基金比例为：{}/{}'.format(lastYearDate, len(result), len(MyFundList)))
    result.reset_index(drop=False, inplace=True)
    result.rename(columns={'jydm': 'thscode'}, inplace=True)
    return result[['thscode', 'Xstyle','Ystyle']]