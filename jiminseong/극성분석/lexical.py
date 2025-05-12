import os
import glob
import pandas as pd
import numpy as np

# ---------------------------
# 1. 임베딩 및 코사인 유사도 계산 함수 정의
# ---------------------------
def get_embedding(token, dim=300, bias=0.0):
    """
    주어진 token에 대해 결정론적 임베딩 벡터 생성.
    - token: 문자열 (n-gram 또는 시드 단어)
    - bias: 추가할 편향 값. 매파 시드는 +0.1, 비둘기파 시드는 -0.1, 일반 n-gram은 0.
    """
    seed = hash(token) % (2**32)
    rng = np.random.RandomState(seed)
    vec = rng.rand(dim)
    return vec + bias

def cosine_similarity(vec1, vec2):
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return np.dot(vec1, vec2) / (norm1 * norm2)

# ---------------------------
# 2. 시드 단어 리스트 및 임베딩 사전 구축 (bias 적용)
# ---------------------------
# 매파 시드 단어 (예시 10개) - bias +0.1
hawkish_seeds = ["인상", "확장", "상향", "투기", "억제", "금리상승", "상회", "채권가격하락", "인플레이션압력", "과열변동성확대"]
hawkish_embeddings = [get_embedding(word, bias=0.1) for word in hawkish_seeds]

# 비둘기파 시드 단어 (예시 10개) - bias -0.1
dovish_seeds = ["인하", "하향", "부진", "회복못하", "금리하락", "하회", "침체", "인플레이션하락", "물가하락", "부동산가격하락"]
dovish_embeddings = [get_embedding(word, bias=-0.1) for word in dovish_seeds]

def compute_polarity_score(ngram):
    """
    주어진 n-gram에 대해 polarity score 계산:
    score = (평균 매파 유사도) / (평균 비둘기파 유사도 + epsilon)
    n-gram은 bias 없이 생성합니다.
    """
    emb = get_embedding(ngram, bias=0.0)
    sims_hawk = [cosine_similarity(emb, seed_emb) for seed_emb in hawkish_embeddings]
    avg_hawk = np.mean(sims_hawk)
    sims_dovish = [cosine_similarity(emb, seed_emb) for seed_emb in dovish_embeddings]
    avg_dovish = np.mean(sims_dovish)
    epsilon = 1e-8
    score = avg_hawk / (avg_dovish + epsilon)
    return score

# ---------------------------
# 3. 폴더 내 CSV 파일 처리 (Lexical Approach 적용)
# ---------------------------
# TF-IDF CSV 파일들이 들어있는 폴더 경로 (실제 경로로 수정)
input_folder = r'C:\Users\abwm2\Desktop\BootCamp\TIL\JIMINSEONG\jiminseong\극성분석\tf idf'  # 예: r"C:\Users\abwm2\Desktop\BootCamp\TIL\JIMINSEONG\jiminseong\극성분석\tf idf"
# 결과를 저장할 새 폴더 생성
output_folder = os.path.join(input_folder, 'lexical_results')
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    print(f"출력 폴더 생성됨: {output_folder}")
else:
    print(f"출력 폴더 존재: {output_folder}")

# 폴더 내 모든 CSV 파일 목록
csv_files = glob.glob(os.path.join(input_folder, '*.csv'))
print(f"총 {len(csv_files)}개의 CSV 파일 발견됨.")

# 각 파일에 대해 Lexical Approach 실행
for file in csv_files:
    print(f"\n===== 파일 처리 시작: {file} =====")
    try:
        # TF-IDF CSV 파일 불러오기 (인코딩은 상황에 맞게 'utf-8-sig' 사용)
        df = pd.read_csv(file, encoding='utf-8-sig')
    except Exception as e:
        print(f"파일 로드 실패: {file}, 에러: {e}")
        continue

    # TF-IDF 파일은 보통 n-gram TF-IDF 수치만 포함합니다.
    # 메타 컬럼(예: "Unnamed")은 제외하고, 모든 컬럼을 n-gram으로 간주합니다.
    ngram_list = [col for col in df.columns if not col.startswith("Unnamed")]
    print(f"총 {len(ngram_list)}개의 n-gram 추출됨.")

    # 각 n-gram에 대해 극성 점수 계산
    results = []
    for ngram in ngram_list:
        score = compute_polarity_score(ngram)
        # 임계값 적용: score > 1.1 → "매파", score < 0.9 → "비둘기파", 그 외는 "중립"
        if score > 1.1:
            label = "매파"
        elif score < 0.9:
            label = "비둘기파"
        else:
            label = "중립"
        results.append({"ngram": ngram, "polarity_score": score, "lexical_label": label})
    
    df_results = pd.DataFrame(results)
    print("극성 점수 분포 통계:")
    print(df_results['polarity_score'].describe())
    print("극성 레이블 분포:")
    print(df_results['lexical_label'].value_counts())
    
    # 결과 CSV 파일 저장 (원본 파일명에 '_lexical' 접미사 추가)
    base_filename = os.path.splitext(os.path.basename(file))[0]
    output_file = os.path.join(output_folder, base_filename + '_lexical.csv')
    df_results.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"결과 파일 저장됨: {output_file}")

print("모든 파일 처리 완료.")

