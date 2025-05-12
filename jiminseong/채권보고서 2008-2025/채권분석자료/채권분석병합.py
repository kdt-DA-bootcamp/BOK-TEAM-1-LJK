import pandas as pd

# 1. 기존 CSV 파일 읽기
df = pd.read_csv("final_features.csv")
# 만약 파일에 헤더가 없다면, 아래와 같이 컬럼 이름을 지정합니다.
# df.columns = ["n-gram"]

# 2. 각 n-gram의 길이(단어 수)를 계산하여 새로운 컬럼에 저장
df["ngram_length"] = df["n-gram"].apply(lambda x: len(x.split()))

# 3. 1-gram부터 5-gram까지 그룹별로 n-gram 리스트를 생성
grouped = {}
for i in range(1, 6):
    grouped[i] = df[df["ngram_length"] == i]["n-gram"].tolist()

# 4. 그룹별 리스트의 길이가 다를 수 있으므로, 가장 긴 리스트의 길이를 찾고 나머지는 빈 문자열로 채웁니다.
max_len = max(len(lst) for lst in grouped.values())
for i in grouped:
    if len(grouped[i]) < max_len:
        grouped[i].extend([""] * (max_len - len(grouped[i])))

# 5. 각 그룹을 컬럼으로 갖는 DataFrame 생성
result_df = pd.DataFrame({
    f"{i}-gram": grouped[i] for i in range(1, 6)
})

# 6. 한 CSV 파일로 저장 (한글 깨짐 방지를 위해 utf-8-sig 인코딩 사용)
result_df.to_csv("organized_final_features.csv", index=False, encoding="utf-8-sig")
print("각 n-gram 길이가 열로 정리된 CSV 파일 'organized_final_features.csv'가 저장되었습니다.")
