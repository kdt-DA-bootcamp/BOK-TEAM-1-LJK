import os
import pandas as pd
from collections import Counter
from konlpy.tag import Okt
from sklearn.feature_extraction.text import TfidfVectorizer

#  1. CSV 파일이 있는 폴더 경로 설정
csv_folder = 'C:/Users/abwm2/Desktop/BootCamp/TIL/JIMINSEONG/jiminseong/의사록 2023 eKoLpy/새 폴더'

#  2. 폴더 내 모든 CSV 파일 가져오기
csv_files = [f for f in os.listdir(csv_folder) if f.endswith('.csv')]

#  3. KoNLPy의 Okt 형태소 분석기 초기화
okt = Okt()

#  4. 형태소 분석 및 표제어(어간) 추출 함수
def tokenize_and_lemmatize(text):
    tokens = okt.pos(text, stem=True)
    return tokens

#  5. 불용어 제거 및 특정 품사만 선택
def filter_tokens(tokens, allowed_pos={"Noun", "Verb", "Adjective", "Adverb"}):
    stopwords = {"의", "가", "은", "는", "이", "있다", "것", "수", "들"}
    filtered = [word for word, pos in tokens if pos in allowed_pos and word not in stopwords]
    return filtered

#  6. n-gram 생성 (1-gram부터 5-gram)
def generate_ngrams(tokens, n_min=1, n_max=5):
    ngrams = []
    for n in range(n_min, n_max + 1):
        ngrams.extend([' '.join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)])
    return ngrams

#  7. 문서 전처리 함수 (형태소 분석 → 불용어 제거 → n-gram 생성)
def process_text(text):
    tokens = tokenize_and_lemmatize(text)
    filtered_tokens = filter_tokens(tokens)
    ngrams = generate_ngrams(filtered_tokens)
    return filtered_tokens, ngrams

#  8. 폴더 내 모든 CSV 파일을 하나씩 처리
for csv_file in csv_files:
    csv_file_path = os.path.join(csv_folder, csv_file)
    
    try:
        # (1) CSV 파일 읽기
        df = pd.read_csv(csv_file_path)

        # (2) 'cleaned_text' 컬럼이 있는지 확인
        if 'cleaned_text' not in df.columns:
            print(f"⚠️ 파일 '{csv_file}' 에 'cleaned_text' 컬럼이 없습니다. 건너뜁니다.")
            continue

        # (3) 형태소 분석 및 n-gram 추출
        df[['tokens', 'ngrams']] = df['cleaned_text'].apply(lambda x: pd.Series(process_text(x)))

        # (4) 전체 코퍼스의 n-gram 빈도 계산
        all_ngrams = [ng for ngram_list in df['ngrams'] for ng in ngram_list]
        ngram_counts = Counter(all_ngrams)

        # (5) 빈도 15회 미만인 n-gram 필터링
        df['ngrams_filtered'] = df['ngrams'].apply(lambda ngrams: [ng for ng in ngrams if ngram_counts[ng] >= 15])

        # (6) 겹치는 n-gram 중 가장 긴 것만 남기기
        def keep_longest_ngrams(ngrams):
            ngrams_sorted = sorted(ngrams, key=lambda x: len(x.split()), reverse=True)
            selected = []
            for ng in ngrams_sorted:
                if not any(ng in other for other in selected):
                    selected.append(ng)
            return selected

        df['ngrams_final'] = df['ngrams_filtered'].apply(keep_longest_ngrams)

        # (7) 최종 n-gram을 하나의 문자열로 결합
        df['ngram_text'] = df['ngrams_final'].apply(lambda x: ' '.join(x))

        # (8) TF-IDF 벡터화 수행
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(df['ngram_text'])
        print(f"파일 '{csv_file}' 처리 완료! TF-IDF 벡터 shape: {X.shape}")

        # (9) 전처리된 데이터를 새로운 CSV 파일로 저장
        output_csv = os.path.join(csv_folder, f"{csv_file[:-4]}_konlpy.csv")  # 기존 파일명 + "_konlpy.csv"
        df.to_csv(output_csv, index=False, encoding="utf-8-sig")
        print(f"저장 완료: {output_csv}\n")

    except Exception as e:
        print(f"❌ 오류 발생: {csv_file} → {e}\n")
