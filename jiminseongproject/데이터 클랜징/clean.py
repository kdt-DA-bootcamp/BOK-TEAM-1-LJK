import pandas as pd
import re

# CSV 파일 로드
df = pd.read_csv("채권분석.csv")

# 정규식: 한글, 영어만 남기기
def clean_text(text):
    return re.sub(r"[]", "", str(text))  # 숫자 특수문자 영어 한글

# **제거할 단어 리스트 (불용어)**
stopwords = []  # 원하는 단어 추가

# 특정 단어 제거 함수
def remove_stopwords(text):
    for word in stopwords:
        text = re.sub(rf"\b{word}\b", "", text, flags=re.IGNORECASE)  # 단어 삭제 (대소문자 무시)
    return " ".join(text.split())  # 불필요한 공백 정리

# 'title' 컬럼 처리
df["title"] = df["title"].apply(clean_text)  # 특수문자, 숫자 제거
df["title"] = df["title"].apply(remove_stopwords)  # 불용어 제거

# 저장
df.to_csv("downloaded_pdfs/debenture_cleaned_data_final.csv", index=False)

print("단어 제거 완료")
