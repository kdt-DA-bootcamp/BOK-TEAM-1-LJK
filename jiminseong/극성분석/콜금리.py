import pandas as pd

# 엑셀 파일 불러오기 (인코딩 문제 없으면)
df = pd.read_excel('KMB_콜금리_일자별.xls')
print(df.head())
print(df.columns.tolist())
