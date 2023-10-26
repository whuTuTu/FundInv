# -*- coding: UTF-8 -*-
"""
@Project ：FundInv
@File    ：BondfundFirstfilter.py
@IDE     ：PyCharm
@Author  ：tutu
@Date    ：2023-10-10 14:52
债券基金筛选，一般只在
"""
from iFinDPy import *  # 同花顺API接口
import pandas as pd
import warnings

from InvokingFunction.GetData import GetbfundbasicData
from InvokingFunction.GetGFunction import exchangedate1, getQtime4liet

warnings.filterwarnings(action='ignore')  # 导入warnings模块，并指定忽略代码运行中的警告信息

def BondFirstFilter(endDate, apikey):
    """
    债券基金筛选
    :param endDate:
    :param apikey:
    :return:
    """
    # 接入同花顺API接口
    thsLogin = THS_iFinDLogin(apikey[0], apikey[1])

    # ------------------------------------------生成相关时间变量--------------------------------------------------------
    beginDate = "20180101"
    repDateQ = getQtime4liet(beginDate, endDate)
    lastRepDate = repDateQ[-1]
    lastRepDate1 = exchangedate1(lastRepDate)
    # ------------------------------------------下面为代码------------------------------------------------------------
    AllFundDF = GetbfundbasicData(lastRepDate, apikey) # 获取全市场数据
    print('基金池总个数为：{}'.format(len(AllFundDF)))

    # 只保留A份额的基金
    filterFundDF = AllFundDF
    filterFundDF['ACEtype'] = filterFundDF['ths_fund_short_name_fund'].str.findall(r'(A|C|E|B)').apply(''.join)
    filterFundDF = filterFundDF[
        filterFundDF['ACEtype'].str.contains('A') | ~filterFundDF['ACEtype'].str.contains('[ACEB]')]
    print('根据ABCE筛选后基金池总个数为：{}'.format(len(filterFundDF)))

    # 剔除被动指数型基金
    filterFundDF = filterFundDF[
        (filterFundDF['ths_invest_type_second_classi_fund'] != '被动指数型债券基金') &
        (filterFundDF['ths_invest_type_second_classi_fund'] != '增强指数型债券基金') &
        (filterFundDF['ths_invest_type_second_classi_fund'] != '混合债券型基金(二级)')
        ]
    print('剔除被动指数型基金和二级债基后基金池总个数为：{}'.format(len(filterFundDF)))

    # 分类为纯债基金和转债基金
    def generate_new_fund_type(row):
        if row['ths_invest_type_second_classi_fund'] in ['中长期纯债券型基金', '短期纯债券型基金',
                                                         '混合债券型基金(一级)']:
            return '纯债基金'
        elif row['ths_invest_type_second_classi_fund'] in ['可转换债券型基金']:
            return '转债基金'

    filterFundDF['Fundtype'] = filterFundDF.apply(generate_new_fund_type, axis=1)

    # 分两类从基金经理的角度统计基金规模（包括共管）
    indtypes = ['纯债基金', '转债基金']
    df1 = filterFundDF.assign(
        ths_fund_manager_current_fund=filterFundDF['ths_fund_manager_current_fund'].str.split(',')).explode(
        'ths_fund_manager_current_fund')
    df1 = df1.reset_index(drop=True)  # 重置索引
    for i in range(2):
        df2 = df1[df1['Fundtype'] == indtypes[i]]  # 筛选某一类的基金df
        df3 = df2.groupby('ths_fund_manager_current_fund')['ths_mergesize_fund'].sum().sort_values(ascending=False)
        top_20_percent = df3.head(int(0.2 * len(df3)))  # 取前20%
        top_20_percent_names = top_20_percent.index.tolist()  # list
        df4 = df2[df2['ths_fund_manager_current_fund'].isin(top_20_percent_names)]
        if i == 0:
            chunzhai = df4
        else:
            zhuanzhai = df4
    cunzhai4list = chunzhai.iloc[:, [0]].values.tolist()
    cunzhai4list = [item for sublist in cunzhai4list for item in sublist]
    chunzhai = filterFundDF[filterFundDF['thscode'].isin(cunzhai4list)]
    zhuanzai4list = zhuanzhai.iloc[:, [0]].values.tolist()
    zhuanzai4list = [item for sublist in zhuanzai4list for item in sublist]
    zhuanzhai = filterFundDF[filterFundDF['thscode'].isin(zhuanzai4list)]

    print('根据基金经理规模筛选后基金池总个数为：{}'.format(len(pd.concat([chunzhai, zhuanzhai]))))
    print('筛选之后纯债基金个数为：{}'.format(len(chunzhai)))
    print('筛选之后转债基金个数为：{}'.format(len(zhuanzhai)))
    chunzhai.to_csv("output/ChunzhaiFund/chunzhai_filter.csv")
    zhuanzhai.to_csv("output/ZhuanzhaiFund/zhuanzhai.csv")
    return [chunzhai, zhuanzhai]
