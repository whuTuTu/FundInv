# -*- coding: UTF-8 -*-
# 注：更新至2023中报
# 载入包
import pandas as pd
import time
import matplotlib.pyplot as plt
from firstfilter import FirstFilter
from short2long import getIndStyle
from IndependentFund import getIndependent
import warnings

warnings.filterwarnings(action='ignore')
warnings.filterwarnings(action='ignore')  # 导入warnings模块，并指定忽略代码运行中的警告信息
plt.rcParams['font.sans-serif'] = ['SimHei']  # 解决中文显示乱码的问题
plt.rcParams['axes.unicode_minus'] = False

start = time.perf_counter()  # 代码开始的时间

# 　------------------------------------------全局变量--------------------------------------------------------

endDate = "20230908"
lastYearDate = "20230630"  # 年报/半年报报告期
lastQuarDate = "20230630"  # 季报报告期
# apikey = ["tfzqsx229", "199d5c"]
apikey = ["tfzq1556", "752862"]

# ------------------------------------------以下为代码--------------------------------------------------------
print("——————————————————————————————————第一次筛选———————————————————————————————————————")
myfund = FirstFilter(endDate, apikey)
print("第一次筛选运行时间：", time.perf_counter() - start, "秒")

print("——————————————————————————————————获取行业主题和风格标签——————————————————————————————")
IndStyle = getIndStyle(lastYearDate, apikey)
print("获取行业主题和风格标签运行时间：", time.perf_counter() - start, "秒")

print("——————————————————————————————————获取共振因子标签———————————————————————————————————")
HDF = getIndependent(lastQuarDate, apikey)
print("获取共振因子标签运行时间：", time.perf_counter() - start, "秒")

# 合并数据
MyFundDF2 = pd.merge(myfund, IndStyle, on='thscode', how='left')
MyFundDF2 = pd.merge(MyFundDF2, HDF, on='thscode', how='left')
MyFundDF2.to_csv("output/MyFundDF2.csv")

print("\n")
types = MyFundDF2['Stable_Count'].dropna().unique().tolist()
for i in range(len(types)):
    fund0 = MyFundDF2[MyFundDF2['Stable_Count'] == types[i]].iloc[:, [0]].values.tolist()
    fund0 = [item for sublist in fund0 for item in sublist]
    print("{}基金的个数为：{}".format(types[i], len(fund0)))

print("\n")
types = MyFundDF2[MyFundDF2['Stable_Count'] == '稳定行业均衡基金']['XStable'].dropna().unique().tolist()
for i in range(len(types)):
    fund0 = MyFundDF2[MyFundDF2['Stable_Count'] == '稳定行业均衡基金'][MyFundDF2['XStable'] == types[i]].iloc[:,
            [0]].values.tolist()
    fund0 = [item for sublist in fund0 for item in sublist]
    print("{}基金的个数为：{}".format(types[i], len(fund0)))

print("\n")
types = MyFundDF2[MyFundDF2['Stable_Count'] == '稳定行业均衡基金']['YStable'].dropna().unique().tolist()
for i in range(len(types)):
    fund0 = MyFundDF2[MyFundDF2['Stable_Count'] == '稳定行业均衡基金'][MyFundDF2['YStable'] == types[i]].iloc[:,
            [0]].values.tolist()
    fund0 = [item for sublist in fund0 for item in sublist]
    print("{}基金的个数为：{}".format(types[i], len(fund0)))

print("\n")
types = MyFundDF2['HCategory'].dropna().unique().tolist()
for i in range(len(types)):
    fund0 = MyFundDF2[MyFundDF2['HCategory'] == types[i]].iloc[:, [0]].values.tolist()
    fund0 = [item for sublist in fund0 for item in sublist]
    print("{}基金的个数为：{}".format(types[i], len(fund0)))
