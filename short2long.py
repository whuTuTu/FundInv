# -*- coding: UTF-8 -*-
"""
@Project ：FundInv 
@File    ：short2long.py
@IDE     ：PyCharm 
@Author  ：tutu
@Date    ：2023-08-23 13:57
短期标签变成长期标签
"""

from IndShort import shortInd
from StyleShort import StyleShort
import pandas as pd
from shortbondfundlabel import getfundcompany, gettime, getlever, getbondtype
import warnings
warnings.filterwarnings(action='ignore')


def getlong(lastYearDate,lastQuarDate, apikey, flag):
    """
    股基的短期标签变成长期标签，包括行业和大小盘和成长价值风格三个标签
    :param lastYearDate: 年报/半年报交易日
    :param apikey: list，["tfzq1556", "752862"]
    :flag: 1-行业；2-大小盘；3-风格；4-共振因子
    :return: 每次返回一个两列的df
    """
    # ------------------------------------------生成相关时间变量--------------------------------------------------------
    beginDate = "20180101"
    # 半年度时间
    beginyear = beginDate[0:4]
    endyear = lastYearDate[0:4]
    monthday = ['0630', '1231']
    aRepDate = [str(i) + j for i in range(int(beginyear), int(endyear) + 1) for j in monthday]
    repDateY = []
    for i in aRepDate:
        if lastYearDate >= i >= beginDate:
            repDateY.append(i)
        else:
            continue
    # 季度时间
    endyear = lastQuarDate[0:4]
    monthday = ['0331','0630','0930','1231']
    aRepDate = [str(i) + j for i in range(int(beginyear), int(endyear) + 1) for j in monthday]
    repDateQ = []
    for i in aRepDate:
        if lastQuarDate >= i >= beginDate:
            repDateQ.append(i)
        else:
            continue
    # ------------------------------------------以下为代码--------------------------------------------------------
    if flag == 1:
        # 行业主题
        for i in range(6):
            df1 = shortInd(repDateY[-(i + 1)], apikey)
            df1.columns = ['thscode', 'INDtype' + repDateY[-(i + 1)]]
            if i == 0:
                INDDF = df1
            else:
                INDDF = pd.merge(INDDF, df1, on='thscode')

        indtype_columns = [col for col in INDDF.columns if col.startswith("INDtype")]
        INDDF['Stable_Count'] = INDDF.apply(lambda row: f"稳定{row[indtype_columns[0]]}" if all(
            row[col] == row[indtype_columns[0]] for col in indtype_columns) else '行业轮动基金', axis=1)

        INDDF.to_csv("output/INDDF_Stable.csv")
        return INDDF[['thscode', 'Stable_Count']]

    elif flag == 2:
        # 大小盘标签
        for i in range(6):
            df1 = StyleShort(repDateY[-(i + 1)], apikey)
            df1.columns = ['thscode', 'Xstyle' + repDateY[-(i + 1)], 'Ystyle' + repDateY[-(i + 1)]]
            if i == 0:
                StyleDF = df1
            else:
                StyleDF = pd.merge(StyleDF, df1, on='thscode')

        X_columns = [col for col in StyleDF.columns if col.startswith("Xstyle")]
        StyleDF['XStable'] = StyleDF.apply(lambda row: f"稳定{row[X_columns[0]]}" if all(
            row[col] == row[X_columns[0]] for col in X_columns) else '风格轮动基金', axis=1)
        Y_columns = [col for col in StyleDF.columns if col.startswith("Ystyle")]
        StyleDF['YStable'] = StyleDF.apply(lambda row: f"稳定{row[Y_columns[0]]}" if all(
            row[col] == row[Y_columns[0]] for col in Y_columns) else '风格轮动基金', axis=1)
        StyleDF.to_csv("output/StyleDF.csv")
        return StyleDF[['thscode', 'XStable']]

    elif flag == 3:
        # 风格标签
        for i in range(6):
            df1 = StyleShort(repDateY[-(i + 1)], apikey)
            df1.columns = ['thscode', 'Xstyle' + repDateY[-(i + 1)], 'Ystyle' + repDateY[-(i + 1)]]
            if i == 0:
                StyleDF = df1
            else:
                StyleDF = pd.merge(StyleDF, df1, on='thscode')

        X_columns = [col for col in StyleDF.columns if col.startswith("Xstyle")]
        StyleDF['XStable'] = StyleDF.apply(lambda row: f"稳定{row[X_columns[0]]}" if all(
            row[col] == row[X_columns[0]] for col in X_columns) else '风格轮动基金', axis=1)
        Y_columns = [col for col in StyleDF.columns if col.startswith("Ystyle")]
        StyleDF['YStable'] = StyleDF.apply(lambda row: f"稳定{row[Y_columns[0]]}" if all(
            row[col] == row[Y_columns[0]] for col in Y_columns) else '风格轮动基金', axis=1)
        StyleDF.to_csv("output/StyleDF.csv")
        return StyleDF[['thscode', 'YStable']]

    elif flag == 4:
        # 共振因子标签（季度数据）
        for i in range(6):
            df1 = gettime(repDateQ[-(i + 1)], apikey)
            df1.columns = ['thscode', 'HCategory' + repDateQ[-(i + 1)]]
            if i == 0:
                df2 = df1
            else:
                df2 = pd.merge(df2, df1, on='thscode')

        indtype_columns = [col for col in df2.columns if col.startswith("HCategory")]
        df2['independent'] = df2.apply(lambda row: f"稳定{row[indtype_columns[0]]}" if all(
            row[col] == row[indtype_columns[0]] for col in indtype_columns) else '轮动基金', axis=1)

        df2.to_csv("output/independent_Stable.csv")
        return df2[['thscode', 'independent']]



def bond4long(lastYearDate,lastQuarDate, apikey, flag):
    """
    债券基金
    :param lastYearDate: 年报/半年报交易日
    :param apikey: list，["tfzq1556", "752862"]
    :flag: 1-基金公司；2-久期；3-杠杆比例；4-债券总类
    :return: 每次返回一个两列的df
    """
    # ------------------------------------------生成相关时间变量--------------------------------------------------------
    beginDate = "20180101"
    # 半年度时间
    beginyear = beginDate[0:4]
    endyear = lastYearDate[0:4]
    monthday = ['0630', '1231']
    aRepDate = [str(i) + j for i in range(int(beginyear), int(endyear) + 1) for j in monthday]
    repDateY = []
    for i in aRepDate:
        if lastYearDate >= i >= beginDate:
            repDateY.append(i)
        else:
            continue
    # 季度时间
    endyear = lastQuarDate[0:4]
    monthday = ['0331','0630','0930','1231']
    aRepDate = [str(i) + j for i in range(int(beginyear), int(endyear) + 1) for j in monthday]
    repDateQ = []
    for i in aRepDate:
        if lastQuarDate >= i >= beginDate:
            repDateQ.append(i)
        else:
            continue
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

        df2.to_csv("output/Company_Stable.csv")
        return df2[['thscode', 'bigcompany']]

    if flag == 2:
        # 久期
        for i in range(6):
            df1 = gettime(repDateQ[-(i + 1)], apikey)
            df1.columns = ['thscode', '久期标签' + repDateQ[-(i + 1)]]
            if i == 0:
                df2 = df1
            else:
                df2 = pd.merge(df2, df1, on='thscode')

        indtype_columns = [col for col in df2.columns if col.startswith("久期标签")]
        df2['Duration'] = df2.apply(lambda row: f"稳定{row[indtype_columns[0]]}" if all(
            row[col] == row[indtype_columns[0]] for col in indtype_columns) else '轮动基金', axis=1)

        df2.to_csv("output/duration_Stable.csv")
        return df2[['thscode', 'Duration']]

    if flag == 3:
        # 杠杆
        for i in range(6):
            df1 = getlever(repDateQ[-(i + 1)], apikey)
            df1.columns = ['thscode', '杠杆比例标签' + repDateQ[-(i + 1)]]
            if i == 0:
                df2 = df1
            else:
                df2 = pd.merge(df2, df1, on='thscode',how='left')

        indtype_columns = [col for col in df2.columns if col.startswith("杠杆比例标签")]
        df2['lever'] = df2.apply(lambda row: f"稳定{row[indtype_columns[0]]}" if all(
            row[col] == row[indtype_columns[0]] for col in indtype_columns) else '轮动基金', axis=1)

        df2.to_csv("output/lever_Stable.csv")
        return df2[['thscode', 'lever']]

    if flag == 4:
        # 债券种类
        for i in range(6):
            df1 = getbondtype(repDateY[-(i + 1)], apikey)
            df1.columns = ['thscode', 'bondfundtype' + repDateQ[-(i + 1)]]
            if i == 0:
                df2 = df1
            else:
                df2 = pd.merge(df2, df1, on='thscode')

        indtype_columns = [col for col in df2.columns if col.startswith("bondfundtype")]
        df2['bondtype'] = df2.apply(lambda row: f"稳定{row[indtype_columns[0]]}" if all(
            row[col] == row[indtype_columns[0]] for col in indtype_columns) else '轮动基金', axis=1)

        df2.to_csv("output/bondtype_Stable.csv")
        return df2[['thscode', 'bondtype']]




