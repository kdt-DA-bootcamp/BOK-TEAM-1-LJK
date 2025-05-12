import pandas as pd
import glob
import os
import re

# 1. 루트 폴더(하위에 여러 폴더가 있을 수 있음)와 결과를 저장할 폴더 설정
root_folder = r'C:\Users\abwm2\Desktop\BootCamp\TIL\JIMINSEONG\jiminseong\극성분석\tf idf'     # CSV 파일들이 흩어져 있는 상위 폴더
output_folder = r'C:\Users\abwm2\Desktop\BootCamp\TIL\JIMINSEONG\jiminseong\극성분석' # 최종 결과물(단일 CSV)을 저장할 폴더
os.makedirs(output_folder, exist_ok=True)

# 2. 모든 CSV 파일 경로를 재귀적으로 수집
csv_files = glob.glob(os.path.join(root_folder, '**', '*.csv'), recursive=True)
print(f"총 {len(csv_files)}개의 CSV 파일을 찾았습니다.")

# 3. 병합할 DataFrame들을 담을 리스트
df_list = []

for file_path in csv_files:
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"{file_path} 로딩 중 에러: {e}")
        continue  # 파일 읽기에 실패하면 넘어감

    # (선택) 파일명에서 숫자만 추출해 컬럼으로 추가
    file_name = os.path.basename(file_path)
    numbers_in_filename = re.findall(r'\d+', file_name)  # 모든 숫자 시퀀스 찾기
    if numbers_in_filename:
        # 예: 첫 번째 숫자(연도 등)만 사용
        df['extracted_number'] = numbers_in_filename[0]
    else:
        df['extracted_number'] = 'Unknown'

    df_list.append(df)

# 4. 전체 DataFrame 병합 및 단일 CSV로 저장
if df_list:
    merged_df = pd.concat(df_list, ignore_index=True)
    
    # 필요하다면 중복 제거, 결측치 처리 등 추가 로직을 수행
    # merged_df.drop_duplicates(inplace=True)
    # merged_df.fillna(...)

    output_csv_path = os.path.join(output_folder, 'merged_data.csv')
    merged_df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
    
    print(f"모든 CSV 파일을 병합한 결과를 '{output_csv_path}'에 저장했습니다.")
else:
    print("병합할 CSV 파일이 없습니다.")
