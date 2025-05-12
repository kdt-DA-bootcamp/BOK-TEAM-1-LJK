import os
import pandas as pd
from transformers import BertTokenizer, BertForMaskedLM
import torch
from konlpy.tag import Okt

# 1. 텍스트 파일들이 있는 폴더 경로 설정
folder_path = r'C:\Users\abwm2\Desktop\BootCamp\TIL\JIMINSEONG\jiminseong\채권보고서 2008-2025\채권분석 텍스트'  # 텍스트 파일들이 있는 폴더 경로

# 2. 폴더 내 모든 텍스트 파일 리스트 가져오기
txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]  # 텍스트 파일만 필터링

# 3. 각 텍스트 파일 읽어서 하나로 합치기
texts = []
for txt_file in txt_files:
    file_path = os.path.join(folder_path, txt_file)
    with open(file_path, 'r', encoding='utf-8') as file:
        texts.extend(file.readlines())  # 각 파일의 내용을 읽어서 리스트에 추가

# 4. KoBERT 모델과 KoBertTokenizer 불러오기
model_name = "monologg/kobert"
tokenizer = BertTokenizer.from_pretrained(model_name)  # KoBERTTokenizer 사용
model = BertForMaskedLM.from_pretrained(model_name)

# 5. GPU 설정 (CUDA 사용 여부 확인)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)  # 모델을 GPU 또는 CPU에 할당

# Okt 객체 생성
okt = Okt()

# 6. 텍스트 전처리 함수 정의 (형태소 단어를 하나의 문장으로 합침)
def process_text(text):
    nouns = okt.nouns(text)  # 명사 추출
    return ' '.join(nouns)

# 7. 형태소로 분리된 텍스트를 하나의 문장으로 합친 후, KoBERT로 처리
processed_texts = []
for text in texts:
    print("Processing:", text[:50])  # 처리 중인 텍스트 일부 출력
    processed_texts.append(process_text(text))

# 8. 처리된 데이터를 CSV 파일로 저장
output_file_path = r'C:\Users\abwm2\Desktop\BootCamp\TIL\JIMINSEONG\jiminseong\채권보고서 2008-2025\processed_data.csv'  # CSV 파일 경로
processed_df = pd.DataFrame(processed_texts, columns=['Processed Text'])

# CSV 파일로 저장
processed_df.to_csv(output_file_path, index=False, encoding='utf-8')

print(f"CSV 파일 저장 완료: {output_file_path}")
