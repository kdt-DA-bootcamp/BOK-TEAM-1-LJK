import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. 데이터 불러오기 (인코딩은 상황에 맞게 'cp949' 또는 'utf-8-sig'로 수정)
df = pd.read_csv('채권분석_극성분류최종결과1.csv', encoding='cp949')

# 2. 전체 컬럼 확인 (디버깅 및 구조 파악용)
print("실제 컬럼 목록:")
print(df.columns.tolist())

# 3. Polarity_Label, hawkish_score, dovish_score 컬럼이 없으면 더미 데이터 생성
if 'Polarity_Label' not in df.columns:
    df['Polarity_Label'] = np.random.choice(['매파', '비둘기파', '중립'], size=len(df))
    print("Polarity_Label 더미 컬럼 생성됨.")

if 'hawkish_score' not in df.columns or 'dovish_score' not in df.columns:
    df['hawkish_score'] = np.random.rand(len(df)) * 100
    df['dovish_score'] = np.random.rand(len(df)) * 100
    print("hawkish_score와 dovish_score 더미 컬럼 생성됨.")

# 4. 'NNG'를 포함하는 n-gram 관련 컬럼이 없으면, 더미 컬럼 생성
ngram_columns = [col for col in df.columns if 'NNG' in col]
if not ngram_columns:
    dummy_cols = ['dummy_NNG1/NNG', 'dummy_NNG2/NNG', 'dummy_NNG3/NNG']
    for col in dummy_cols:
        df[col] = np.random.randint(0, 10, size=len(df))
    ngram_columns = dummy_cols
    print("n-gram 관련 더미 컬럼 생성됨:", ngram_columns)

# 5. 극성 분포 확인 및 출력
sentiment_counts = df['Polarity_Label'].value_counts()
print("\n극성 분포:")
print(sentiment_counts)

# 6. 극성별 평균 점수 계산 및 출력
avg_scores = df.groupby('Polarity_Label')[['hawkish_score', 'dovish_score']].mean()
print("\n극성별 평균 점수:")
print(avg_scores)

# 7. 박스플롯 시각화 (매파, 비둘기파 점수 분포)
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
df.boxplot(column='hawkish_score', by='Polarity_Label')
plt.title("극성별 매파 점수 분포")
plt.suptitle("")
plt.xlabel("극성")
plt.ylabel("매파 점수")

plt.subplot(1, 2, 2)
df.boxplot(column='dovish_score', by='Polarity_Label')
plt.title("극성별 비둘기파 점수 분포")
plt.suptitle("")
plt.xlabel("극성")
plt.ylabel("비둘기파 점수")
plt.tight_layout()
plt.show()

# 8. 극성별 문서 수 막대그래프 시각화
plt.figure(figsize=(8, 6))
sentiment_counts.plot(kind='bar', color=['blue', 'orange', 'green'])
plt.title("극성 분포 (매파, 비둘기파, 중립)")
plt.xlabel("극성 레이블")
plt.ylabel("문서 수")
plt.xticks(rotation=0)
plt.grid(axis='y')
plt.show()

# 9. n-gram 관련 세부 통계: 'NNG' 포함 컬럼들의 빈도 합계 계산 및 출력
ngram_sums = df[ngram_columns].sum().sort_values(ascending=False)
print("\n상위 n-gram 빈도 합계:")
print(ngram_sums.head(10))

# 10. 분석 결과를 CSV 파일로 저장
output_filename = '채권분석_극성분류_세부결과.csv'
df.to_csv(output_filename, index=False, encoding='cp949')
print(f"\n분석 결과가 '{output_filename}'로 저장되었습니다.")

