# -*- coding: UTF-8 -*-
"""
@Project :FundInv
@File    :test.py
@IDE     :Pycharm
@Author  :tutu
@Date    :2023/11/15 14:34
"""
# from iFinDPy import *  # 同花顺API接口
# import configparser
#
# from InvokingFunction.GetShortbondfundLabel import getbondtype, getbondtype4test
#
# config = configparser.ConfigParser()
# config.read("config.ini", encoding="utf-8")
# apikey = [config.get("apikey", "ID1"),config.get("apikey", "password1")]
# df1 = getbondtype4test('20230630', apikey)
# df1.to_csv("test1.csv")

import pandas as pd

StyleDF = pd.DataFrame({
    '2018Q1': ['成长', '价值', '成长', '成长'],
    '2018Q2': ['成长', '价值', '价值', '成长'],
    '2018Q3': ['成长', '成长', '价值', '成长'],
    '2018Q4': ['成长', '价值', '价值', '成长'],
    '2019Q1': ['成长', '价值', '价值', '成长']
})

X_columns = ['2018Q1', '2018Q2', '2018Q3', '2018Q4', '2019Q1']

StyleDF['风格标签'] = StyleDF.apply(lambda row: "稳定"+row[X_columns].value_counts().index[0] if row[X_columns].value_counts().iloc[0] >= 4 else '风格轮动基金', axis=1)

print(StyleDF)