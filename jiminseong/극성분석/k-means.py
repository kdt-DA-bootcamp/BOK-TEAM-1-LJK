import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report

# 1. 데이터 불러오기 (cp949 인코딩 사용)
data_path = r'C:\Users\abwm2\Desktop\BootCamp\TIL\JIMINSEONG\jiminseong\극성분석\merged_data.csv'
df = pd.read_csv(data_path, encoding='cp949')

# 2. 분석에 사용할 텍스트 컬럼 선택
# 여기서는 'n_gram' 컬럼이 있으면 사용, 없으면 'tokenized_text' 컬럼 사용 (필요에 따라 수정)
text_column = 'n_gram' if 'n_gram' in df.columns else 'tokenized_text'
if text_column not in df.columns:
    raise ValueError("분석에 사용할 텍스트 컬럼이 없습니다. 컬럼명을 확인하세요.")

# 3. TF-IDF 벡터화
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df[text_column])

# 4. 비지도 학습: KMeans 클러스터링으로 pseudo-label 생성
k = 3  # 클러스터 수 (도메인에 맞게 변경)
kmeans = KMeans(n_clusters=k, random_state=42)
df['pseudo_label'] = kmeans.fit_predict(X)

print("생성된 pseudo_label 분포:")
print(df['pseudo_label'].value_counts())

# 5. train/test 분할 (원본 DataFrame도 함께 분할하여 인덱스 보존)
df_train, df_test = train_test_split(df, test_size=0.2, random_state=42)
X_train = vectorizer.transform(df_train[text_column])
y_train = df_train['pseudo_label']
X_test = vectorizer.transform(df_test[text_column])
y_test = df_test['pseudo_label']

# 6. Naive Bayes 모델 학습
nb_model = MultinomialNB()
nb_model.fit(X_train, y_train)

# 7. 테스트 데이터에 대해 예측 수행
y_pred = nb_model.predict(X_test)
df_test = df_test.copy()  # 원본 DataFrame 보호
df_test['predicted_label'] = y_pred

# 8. 평가 결과 출력 (옵션)
print("Naive Bayes 분류 모델 평가 결과:")
print(classification_report(y_test, y_pred))

# 9. 테스트 결과를 CSV 파일로 저장 (cp949 인코딩 사용)
output_csv_path = r'C:\Users\abwm2\Desktop\BootCamp\TIL\JIMINSEONG\jiminseong\극성분석\test_results_with_predictions.csv'
df_test.to_csv(output_csv_path, index=False, encoding='cp949')
print(f"테스트 결과와 예측값이 저장된 CSV 파일: {output_csv_path}")
