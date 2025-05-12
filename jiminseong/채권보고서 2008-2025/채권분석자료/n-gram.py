import pandas as pd
from konlpy.tag import Okt
from sklearn.feature_extraction.text import CountVectorizer

# 1. CSV 파일 로드
df = pd.read_csv(r'C:\Users\abwm2\Desktop\BootCamp\TIL\JIMINSEONG\jiminseong\채권보고서 2008-2025\processed_data.csv')
# 'text' 컬럼이 없으면 첫번째 컬럼 사용
if 'text' not in df.columns:
    text_col = df.columns[0]
else:
    text_col = 'text'
    
texts = df[text_col].dropna().tolist()
print("전체 문서 수:", len(texts))

# 2. 토큰화 및 품사 태깅
okt = Okt()

def tokenize_and_filter(text):
    # KoNLPy를 이용한 토큰화 및 품사 태깅 (norm=True, stem=True)
    tokens = okt.pos(text, norm=True, stem=True)
    # 사용할 품사: 명사, 형용사, 동사, 부사 및 부정표현 포함
    valid_pos = ['Noun', 'Adjective', 'Verb', 'Adverb']
    filtered = [word for word, pos in tokens if pos in valid_pos or 'Neg' in pos]
    return filtered

# 각 문서에 대해 토큰화 및 필터링 수행
tokenized_texts = [" ".join(tokenize_and_filter(text)) for text in texts]

# 3. n-gram 생성 (1-gram ~ 5-gram) 및 빈도수(min_df=15) 필터링
vectorizer = CountVectorizer(ngram_range=(1, 5), min_df=15)
X = vectorizer.fit_transform(tokenized_texts)
features = vectorizer.get_feature_names_out()
print("추출된 n-gram 개수:", len(features))

# 4. 중복 n-gram 제거 (다른 n-gram에 포함되어 있고 더 짧은 경우 제거)
final_features = []
for feat in features:
    if not any((feat in other_feat and feat != other_feat and len(feat) < len(other_feat)) 
               for other_feat in features):
        final_features.append(feat)

print("중복 제거 후 최종 n-gram 개수:", len(final_features))

# 5. DataFrame으로 변환하여 데이터 결과 확인 및 CSV 파일로 저장
df_features = pd.DataFrame(final_features, columns=["n-gram"])
print("\n최종 n-gram 데이터 일부:")
print(df_features.head(10))  # 상위 10개 항목을 출력

# CSV 파일로 저장 (현재 작업 디렉터리에 저장됨)
df_features.to_csv("final_features.csv", index=False, encoding="utf-8-sig")
print("\n최종 n-gram 데이터가 'final_features.csv' 파일로 저장되었습니다.")
