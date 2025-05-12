import pandas as pd

# 1. final_features.csv 파일 읽기
df = pd.read_csv("final_features.csv")

# 2. 각 n-gram의 단어 수(즉, n-gram 길이)를 계산합니다.
df["ngram_length"] = df["n-gram"].apply(lambda x: len(x.split()))

# 3. n-gram 길이에 따라 데이터를 분리하여 각각 CSV 파일로 저장합니다.
for i in range(1, 6):
    df_i = df[df["ngram_length"] == i].drop(columns=["ngram_length"])
    filename = f"final_features_{i}gram.csv"
    df_i.to_csv(filename, index=False, encoding="utf-8-sig")
    print(f"{i}-gram 데이터가 '{filename}' 파일로 저장되었습니다.")
