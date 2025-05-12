import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# 1. CSV 파일 불러오기 (cp949 인코딩)
input_csv_path = 'final_data_with_sentiment.csv'
df = pd.read_csv(input_csv_path, encoding='cp949')

# 2. 분석에 사용할 텍스트 컬럼 지정 (여기서는 n_gram 컬럼 사용)
n_gram_column = 'n_gram'
if n_gram_column not in df.columns:
    raise ValueError(f"'{n_gram_column}' 컬럼이 존재하지 않습니다. 컬럼명을 확인하세요.")

# 3. 텍스트 데이터를 TF-IDF 벡터화
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df[n_gram_column].astype(str))

# 4. KMeans 클러스터링 실행
# 클러스터 수는 도메인에 맞게 조정 (예시로 3개 사용)
k = 3
kmeans = KMeans(n_clusters=k, random_state=42)
df['cluster_label'] = kmeans.fit_predict(X)

# 5. 클러스터 분포 확인
print("각 클러스터에 속한 데이터 수:")
print(df['cluster_label'].value_counts())

# 6. 결과 CSV 파일로 저장 (cp949 인코딩)
output_csv_path = 'final_data_with_kmeans.csv'
df.to_csv(output_csv_path, index=False, encoding='cp949')
print(f"KMeans 클러스터링 결과가 저장되었습니다: {output_csv_path}")
