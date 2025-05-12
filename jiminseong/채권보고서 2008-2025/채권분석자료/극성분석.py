import pandas as pd

# 저장된 클러스터링 결과 불러오기
data = pd.read_csv('채권분석_클러스터링결과.csv')

# 클러스터 번호 확인
print(data['Sentiment_Cluster'].value_counts())

# 클러스터별로 대표 문서 샘플링
for cluster_num in range(3):
    print(f"\n클러스터 {cluster_num}의 샘플 문서 인덱스:")
    sample_docs = data[data['Sentiment_Cluster'] == cluster_num].sample(min(5, len(data)))
    print(sample_docs.index.tolist())
# 클러스터 번호를 극성으로 변경하기 위한 맵핑
sentiment_mapping = {0: '부정', 1: '긍정', 2: '중립'}

# 기존 데이터에 극성 레이블 추가
data['Sentiment_Label'] = data['Sentiment_Cluster'].map(sentiment_mapping)

# 극성이 추가된 최종 결과 저장
data.to_csv('채권분석_극성분류최종결과.csv', index=False, encoding='utf-8-sig')

print("극성 레이블이 추가된 최종 결과가 저장되었습니다.")
