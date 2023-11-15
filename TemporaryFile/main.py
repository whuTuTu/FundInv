# 导入库
from ydata_profiling import ProfileReport
import pandas as pd
# 读取数据
df = pd.read_csv('housing.csv')
# 自动生成数据探索报告
profile = ProfileReport(df, title="Profiling Report")
profile
