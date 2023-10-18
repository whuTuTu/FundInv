# -*- coding: UTF-8 -*-
"""
@Project ：FundInv
@File    ：ConcentrationRatio.py
@IDE     ：PyCharm
@Author  ：tutu
@Date    ：2023-09-26 13:26
"""

# 载入包
from iFinDPy import *  # 同花顺API接口
import pandas as pd
import warnings
warnings.filterwarnings(action='ignore')  # 导入warnings模块，并指定忽略代码运行中的警告信息

def getIndependent(lastQuarDate, apikey):
    """
    :param lastQuarDate: 季报
    :param apikey: list，["tfzq1556", "752862"]
    :return: df
    """
    # 接入同花顺API接口
    thsLogin = THS_iFinDLogin(apikey[0], apikey[1])

    try:
        CDF = pd.read_csv("input/Con" + lastQuarDate + ".csv")
        CDF.drop('Unnamed: 0', axis=1, inplace=True)
    except FileNotFoundError:
        print("本地文件不存在，尝试从接口获取数据...")