# -*- coding: UTF-8 -*-
"""
@Project ：FundInv 
@File    ：Short2Long.py
@IDE     ：PyCharm 
@Author  ：tutu
@Date    ：2023-08-23 13:57
短期标签变成长期标签
"""

from InvokingFunction.GetShortstockfundLabel import getindustry, getstyle, getindependent, getCR
from InvokingFunction.GetGFunction import getHYtime4list, getQtime4liet
from InvokingFunction.GetShortbondfundLabel import getfundcompany, getbondtype, getlever, getduration
import pandas as pd
import os
import warnings
warnings.filterwarnings(action='ignore')
# 更改相对路径
path = "D:\TFCode\FundInv"
os.chdir(path)

def Getstockfund4Long(lastYearDate, lastQuarDate, apikey, flag):
    """
    股基的短期标签变成长期标签，包括行业和大小盘和成长价值风格三个标签
    :param lastYearDate: 年报/半年报交易日
    :param apikey: list，["tfzq1556", "752862"]
    :flag: 1-行业；2-大小盘；3-风格；4-共振因子， 5-集中度
    :return: 每次返回一个两列的df
    """
    # ------------------------------------------生成相关时间变量--------------------------------------------------------
    beginDate = "20180101"
    repDateHY = getHYtime4list(beginDate, lastYearDate)
    repDateQ = getQtime4liet(beginDate, lastQuarDate)
    # ------------------------------------------以下为代码------------------------------------------------------------
    if flag == 1:
        # 行业主题
        for i in range(6):
            df1 = getindustry(repDateHY[-(i + 1)], apikey)
            df1.columns = ['thscode', 'INDtype' + repDateHY[-(i + 1)]]
            if i == 0:
                INDDF = df1
            else:
                INDDF = pd.merge(INDDF, df1, on='thscode')

        indtype_columns = [col for col in INDDF.columns if col.startswith("INDtype")]
        INDDF['行业标签'] = INDDF.apply(lambda row: f"稳定{row[indtype_columns[0]]}" if all(
            row[col] == row[indtype_columns[0]] for col in indtype_columns) else '行业轮动基金', axis=1)

        INDDF.to_csv("output/StockFund/industry_Stable.csv")
        return INDDF[['thscode', '行业标签']]

    elif flag == 2:
        # 大小盘标签
        for i in range(6):
            df1 = getstyle(repDateHY[-(i + 1)], apikey)
            df1.columns = ['thscode', 'Xstyle' + repDateHY[-(i + 1)], 'Ystyle' + repDateHY[-(i + 1)]]
            if i == 0:
                StyleDF = df1
            else:
                StyleDF = pd.merge(StyleDF, df1, on='thscode')

        X_columns = [col for col in StyleDF.columns if col.startswith("Xstyle")]
        StyleDF['大小盘标签'] = StyleDF.apply(lambda row: f"稳定{row[X_columns[0]]}" if all(
            row[col] == row[X_columns[0]] for col in X_columns) else '风格轮动基金', axis=1)
        StyleDF.to_csv("output/StockFund/marketvalue_Stable.csv")
        return StyleDF[['thscode', '大小盘标签']]

    elif flag == 3:
        # 风格标签
        for i in range(6):
            df1 = getstyle(repDateHY[-(i + 1)], apikey)
            df1.columns = ['thscode', 'Xstyle' + repDateHY[-(i + 1)], 'Ystyle' + repDateHY[-(i + 1)]]
            if i == 0:
                StyleDF = df1
            else:
                StyleDF = pd.merge(StyleDF, df1, on='thscode')

        Y_columns = [col for col in StyleDF.columns if col.startswith("Ystyle")]
        StyleDF['风格标签'] = StyleDF.apply(lambda row: f"稳定{row[Y_columns[0]]}" if all(
            row[col] == row[Y_columns[0]] for col in Y_columns) else '风格轮动基金', axis=1)
        StyleDF.to_csv("output/StockFund/style_Stable.csv")
        return StyleDF[['thscode', '风格标签']]

    elif flag == 4:
        # 共振因子标签（季度数据）
        for i in range(6):
            df1 = getindependent(repDateQ[-(i + 1)], apikey)
            df1.columns = ['thscode', 'HCategory' + repDateQ[-(i + 1)]]
            if i == 0:
                df2 = df1
            else:
                df2 = pd.merge(df2, df1, on='thscode')

        indtype_columns = [col for col in df2.columns if col.startswith("HCategory")]
        df2['共振因子标签'] = df2.apply(lambda row: f"稳定{row[indtype_columns[0]]}" if all(
            row[col] == row[indtype_columns[0]] for col in indtype_columns) else '轮动基金', axis=1)

        df2.to_csv("output/StockFund/independence_Stable.csv")
        return df2[['thscode', '共振因子标签']]

    elif flag == 5:
        # 集中度标签
        # 共振因子标签（季度数据）
        for i in range(6):
            df1 = getCR(repDateQ[-(i + 1)], apikey)
            df1.columns = ['thscode', 'cr' + repDateQ[-(i + 1)]]
            if i == 0:
                df2 = df1
            else:
                df2 = pd.merge(df2, df1, on='thscode')

        indtype_columns = [col for col in df2.columns if col.startswith("cr")]
        df2['集中度标签'] = df2.apply(lambda row: f"稳定{row[indtype_columns[0]]}" if all(
            row[col] == row[indtype_columns[0]] for col in indtype_columns) else '轮动基金', axis=1)
        df2.to_csv("output/StockFund/CR_Stable.csv")
        return df2[['thscode', '集中度标签']]


def Getbondfund4Long(lastYearDate, lastQuarDate, apikey, flag):
    """
    债券基金
    :param lastYearDate: 年报/半年报交易日
    :param apikey:
    :flag: 1-基金公司；2-久期；3-杠杆比例；4-债券种类
    :return: 每次返回一个两列的df
    """
    # ------------------------------------------生成相关时间变量--------------------------------------------------------
    beginDate = "20180101"
    repDateHY = getHYtime4list(beginDate, lastYearDate)
    repDateQ = getQtime4liet(beginDate, lastQuarDate)
    # ------------------------------------------以下为代码--------------------------------------------------------
    if flag == 1:
        # 基金公司
        for i in range(6):
            df1 = getfundcompany(repDateQ[-(i + 1)], apikey)
            df1.columns = ['thscode', '基金公司标签' + repDateQ[-(i + 1)]]
            if i == 0:
                df2 = df1
            else:
                df2 = pd.merge(df2, df1, on='thscode')

        indtype_columns = [col for col in df2.columns if col.startswith("基金公司标签")]
        df2['bigcompany'] = df2.apply(lambda row: f"稳定{row[indtype_columns[0]]}" if all(
            row[col] == row[indtype_columns[0]] for col in indtype_columns) else '轮动基金', axis=1)

        df2.to_csv("output/ChunzhaiFund/Company_stable.csv")
        return df2[['thscode', 'bigcompany']]

    if flag == 2:
        # 久期
        for i in range(6):
            df1 = getduration(repDateQ[-(i + 1)], apikey)
            df1.columns = ['thscode', '久期标签' + repDateQ[-(i + 1)]]
            if i == 0:
                df2 = df1
            else:
                df2 = pd.merge(df2, df1, on='thscode')

        indtype_columns = [col for col in df2.columns if col.startswith("久期标签")]
        df2['Duration'] = df2.apply(lambda row: f"稳定{row[indtype_columns[0]]}" if all(
            row[col] == row[indtype_columns[0]] for col in indtype_columns) else '轮动基金', axis=1)

        df2.to_csv("output/ChunzhaiFund/duration_stable.csv")
        return df2[['thscode', 'Duration']]

    if flag == 3:
        # 杠杆
        for i in range(6):
            df1 = getlever(repDateQ[-(i + 1)], apikey)
            df1.columns = ['thscode', '杠杆比例标签' + repDateQ[-(i + 1)]]
            if i == 0:
                df2 = df1
            else:
                df2 = pd.merge(df2, df1, on='thscode', how='left')

        indtype_columns = [col for col in df2.columns if col.startswith("杠杆比例标签")]
        df2['lever'] = df2.apply(lambda row: f"稳定{row[indtype_columns[0]]}" if all(
            row[col] == row[indtype_columns[0]] for col in indtype_columns) else '轮动基金', axis=1)

        df2.to_csv("output/ChunzhaiFund/lever_stable.csv")
        return df2[['thscode', 'lever']]

    if flag == 4:
        # 债券种类
        for i in range(6):
            df1 = getbondtype(repDateHY[-(i + 1)], apikey)
            df1.columns = ['thscode', 'bondfundtype' + repDateHY[-(i + 1)]]
            if i == 0:
                df2 = df1
            else:
                df2 = pd.merge(df2, df1, on='thscode')

        indtype_columns = [col for col in df2.columns if col.startswith("bondfundtype")]
        df2['bondtype'] = df2.apply(lambda row: f"稳定{row[indtype_columns[0]]}" if all(
            row[col] == row[indtype_columns[0]] for col in indtype_columns) else '轮动基金', axis=1)

        df2.to_csv("output/ChunzhaiFund/bondtype_stable.csv")
        return df2[['thscode', 'bondtype']]