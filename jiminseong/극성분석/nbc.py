import os
import glob
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.preprocessing import LabelEncoder

def read_csv_with_encodings(file, encodings=["cp949", "utf-8-sig", "euc-kr"]):
    """여러 인코딩을 순차적으로 시도하여 CSV 파일을 읽는 함수."""
    for enc in encodings:
        try:
            return pd.read_csv(file, encoding=enc)
        except UnicodeDecodeError as e:
            print(f"{file} 에서 인코딩 {enc} 실패: {e}")
    raise UnicodeDecodeError(f"{file} 파일을 지정한 인코딩으로 읽을 수 없습니다.")

# 1. CSV 파일 81개 읽어오기 (CSV 파일만 선택)
csv_files = glob.glob(r"C:\Users\abwm2\Desktop\BootCamp\TIL\JIMINSEONG\jiminseong\극성분석\tf idf\*.csv")
csv_files = [file for file in csv_files if os.path.isfile(file)]
print("총 CSV 파일 수:", len(csv_files))

dataframes = [read_csv_with_encodings(file) for file in csv_files]
df = pd.concat(dataframes, ignore_index=True)

# 2. 전처리 및 레이블 생성
df = df.dropna(subset=['ngram', 'tfidf'])
df['label'] = df['tfidf'].apply(lambda x: 'hawkish' if x > 0 else ('dovish' if x < 0 else 'neutral'))
df = df[df['label'] != 'neutral']

# 3. n-gram 특징 추출 (1~5-gram), min_df=5로 희귀 n-gram 제외
vectorizer = CountVectorizer(ngram_range=(1, 5), min_df=5)
X = vectorizer.fit_transform(df['ngram'])
y = df['label']

# 4. 학습/테스트 데이터 분할 (9:1 비율, 인덱스 보존)
train_idx, test_idx = train_test_split(df.index, test_size=0.1, random_state=42, stratify=df['label'])
X_train = X[train_idx]
X_test = X[test_idx]
y_train = df.loc[train_idx, 'label']
y_test = df.loc[test_idx, 'label']

le = LabelEncoder()
y_train_enc = le.fit_transform(y_train)
y_test_enc = le.transform(y_test)

# 5. Bagging을 통한 Naive Bayes 분류기 학습 (30회 반복, 테스트 데이터 평가)
n_bags = 30
ensemble_prob_test = np.zeros((X_test.shape[0], 2))

for i in range(n_bags):
    sample_indices = np.random.choice(len(train_idx), size=len(train_idx), replace=True)
    bootstrap_idx = np.array(train_idx)[sample_indices]
    X_train_sample = X[bootstrap_idx]
    y_train_sample = df.loc[bootstrap_idx, 'label']
    y_train_sample_enc = le.transform(y_train_sample)
    
    model = MultinomialNB()
    model.fit(X_train_sample, y_train_sample_enc)
    ensemble_prob_test += model.predict_proba(X_test)

ensemble_prob_test /= n_bags

print("레이블 매핑:", dict(enumerate(le.classes_)))

if len(le.classes_) < 2 or 'dovish' not in le.classes_:
    print("Warning: 'dovish' 레이블이 존재하지 않습니다. 모든 예측 결과를 'hawkish'로 처리합니다.")
    predicted_labels_test = np.array(['hawkish'] * len(y_test))
else:
    hawkish_index = list(le.classes_).index('hawkish')
    dovish_index = list(le.classes_).index('dovish')
    polarity_scores_test = np.divide(
        ensemble_prob_test[:, hawkish_index],
        ensemble_prob_test[:, dovish_index],
        out=np.zeros_like(ensemble_prob_test[:, hawkish_index]),
        where=ensemble_prob_test[:, dovish_index] != 0
    )
    threshold = 1.0
    predicted_labels_test = np.where(polarity_scores_test > threshold, 'hawkish', 'dovish')

accuracy = accuracy_score(y_test, predicted_labels_test)
if len(le.classes_) < 2 or 'dovish' not in le.classes_:
    precision = 100.0
    recall = 100.0
else:
    precision = precision_score(y_test, predicted_labels_test, pos_label='hawkish', average='binary') * 100
    recall = recall_score(y_test, predicted_labels_test, pos_label='hawkish', average='binary') * 100

print("Ensemble NBC 성능 (테스트 데이터):")
print("정확도: {:.2f}%".format(accuracy * 100))
print("Precision (hawkish): {:.2f}%".format(precision))
print("Recall (hawkish): {:.2f}%".format(recall))

# 6. 전체 데이터에 대해 앙상블 예측 수행
ensemble_prob_full = np.zeros((X.shape[0], 2))
for i in range(n_bags):
    sample_indices = np.random.choice(len(train_idx), size=len(train_idx), replace=True)
    bootstrap_idx = np.array(train_idx)[sample_indices]
    X_train_sample = X[bootstrap_idx]
    y_train_sample = df.loc[bootstrap_idx, 'label']
    y_train_sample_enc = le.transform(y_train_sample)
    
    model = MultinomialNB()
    model.fit(X_train_sample, y_train_sample_enc)
    ensemble_prob_full += model.predict_proba(X)

ensemble_prob_full /= n_bags

if len(le.classes_) < 2 or 'dovish' not in le.classes_:
    predicted_labels_full = np.array(['hawkish'] * X.shape[0])
else:
    polarity_scores_full = np.divide(
        ensemble_prob_full[:, hawkish_index],
        ensemble_prob_full[:, dovish_index],
        out=np.zeros_like(ensemble_prob_full[:, hawkish_index]),
        where=ensemble_prob_full[:, dovish_index] != 0
    )
    predicted_labels_full = np.where(polarity_scores_full > threshold, 'hawkish', 'dovish')

df['predicted_label'] = predicted_labels_full

if len(le.classes_) >= 2 and 'dovish' in le.classes_:
    feature_names = vectorizer.get_feature_names_out()
    log_prob_diff = model.feature_log_prob_[hawkish_index] - model.feature_log_prob_[dovish_index]
    top_n = 20
    top_indices = np.argsort(log_prob_diff)[-top_n:]
    print("\n매파(hawkish)를 시사하는 상위 n-gram:")
    for idx in top_indices:
        print(f"{feature_names[idx]}: {log_prob_diff[idx]:.4f}")
else:
    print("\n두 레이블이 모두 존재하지 않아 n-gram log 확률 차이를 계산하지 않습니다.")

output_path = r"C:\Users\abwm2\Desktop\BootCamp\TIL\JIMINSEONG\merged_output.csv"
df.to_csv(output_path, index=False)
print(f"\n최종 병합 CSV 파일이 저장되었습니다: {output_path}")
