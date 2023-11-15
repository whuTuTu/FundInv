# -*- coding: UTF-8 -*-
"""
@Project :FundInv
@File    :test.py
@IDE     :Pycharm
@Author  :tutu
@Date    :2023/11/15 14:34
"""
from iFinDPy import *  # 同花顺API接口
import configparser

from InvokingFunction.GetShortbondfundLabel import getbondtype

config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")
apikey = [config.get("apikey", "ID1"),config.get("apikey", "password1")]
df1 = getbondtype('20230630', apikey)
df1.to_csv("test1.csv")