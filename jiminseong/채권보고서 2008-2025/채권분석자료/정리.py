import pandas as pd

# 1. TF-IDF 결과 파일 읽기 (인코딩 문제 처리)
try:
    df_tfidf = pd.read_csv("tfidf_result.csv", encoding="utf-8-sig")
except Exception as e:
    print("utf-8-sig 인코딩으로 읽기 실패, cp949로 시도합니다:", e)
    df_tfidf = pd.read_csv("tfidf_result.csv", encoding="cp949")

print("TF-IDF DataFrame 로드됨. Shape:", df_tfidf.shape)

# 2. 각 열마다 0이 아닌 값은 위쪽, 0은 아래쪽으로 재정렬
df_sorted = pd.DataFrame()

for col in df_tfidf.columns:
    series = df_tfidf[col]
    # 0이 아닌 값들 추출
    nonzeros = series[series != 0]
    # 0인 값들 추출 (숫자 0 그대로)
    zeros = series[series == 0]
    # nonzeros를 먼저, zeros를 그 뒤에 이어 붙임
    sorted_list = nonzeros.tolist() + zeros.tolist()
    df_sorted[col] = pd.Series(sorted_list)

# 3. 재정렬된 DataFrame을 CSV 파일로 저장 (utf-8-sig 인코딩)
df_sorted.to_csv("tfidf_sorted_with_zeros.csv", index=False, encoding="utf-8-sig")
print("정렬된 TF-IDF 결과가 'tfidf_sorted_with_zeros.csv'로 저장되었습니다.")
