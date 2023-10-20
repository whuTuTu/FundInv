import pandas as pd

from getfunction import df2list

cunzhai4df = pd.read_csv("output/chunzhai.csv")
cunzhai4df.drop('Unnamed: 0', axis=1, inplace=True)
print(cunzhai4df.iloc[:,[0]])
print(df2list(cunzhai4df.iloc[:,[0]]))