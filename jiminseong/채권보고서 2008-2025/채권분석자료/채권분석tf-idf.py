import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

# 1. 원본 문서 데이터 로드 (processed_data.csv)
df_docs = pd.read_csv("processed_data.csv")
# 'text' 컬럼이 있으면 사용, 없으면 첫 번째 컬럼 사용
if 'text' in df_docs.columns:
    documents = df_docs['text'].dropna().tolist()
else:
    documents = df_docs[df_docs.columns[0]].dropna().tolist()
print("문서 수:", len(documents))

# 2. vocabulary로 사용할 n-gram 목록 로드 ("채권분석 n- gram.csv")
df_vocab = pd.read_csv("채권분석 n- gram.csv")
# 'n-gram' 컬럼이 있으면 사용, 없으면 첫 번째 컬럼 사용
if 'n-gram' in df_vocab.columns:
    vocab = df_vocab['n-gram'].dropna().tolist()
else:
    vocab = df_vocab[df_vocab.columns[0]].dropna().tolist()
vocab = list(set(vocab))  # 중복 제거
print("사용할 n-gram 개수(보카뷸러리):", len(vocab))

# 3. TF-IDF 계산: vocabulary를 사용하여 TF-IDF 행렬 생성
vectorizer = TfidfVectorizer(vocabulary=vocab)
tfidf_matrix = vectorizer.fit_transform(documents)
print("TF-IDF 행렬의 크기:", tfidf_matrix.shape)

# 4. TF-IDF 행렬을 DataFrame으로 변환
df_tfidf = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())

# 5. 세로(특징이 행, 문서가 열)로 보기 위해 전치(transpose)
df_tfidf_transposed = df_tfidf.transpose()

# 6. 전치된 결과를 CSV 파일로 저장
df_tfidf_transposed.to_csv("tfidf_result_vertical.csv", encoding="utf-8-sig")
print("세로로 정리된 TF-IDF 결과가 'tfidf_result_vertical.csv' 파일로 저장되었습니다.")

# (선택) 일부 결과 출력
print(df_tfidf_transposed.head(10))
