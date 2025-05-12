import pandas as pd

# 기존 극성분류 최종 결과 파일 로드
data = pd.read_csv('채권분석_극성분류최종결과.csv')

# 극성별 문서 수 요약 (예: {'긍정': 21, '중립': 6468, '부정': 41})
sentiment_summary = data['Sentiment_Label'].value_counts().to_dict()

# 저장할 파일명 지정
output_filename = '채권분석_극성분류최종결과_with_summary.csv'

# 파일 상단에 주석으로 극성 요약 정보를 포함하여 저장
with open(output_filename, 'w', encoding='utf-8-sig') as f:
    f.write('# 극성 요약: ' + str(sentiment_summary) + '\n')
    data.to_csv(f, index=False)

print(f"극성 요약이 포함된 결과가 '{output_filename}'로 저장되었습니다.")
