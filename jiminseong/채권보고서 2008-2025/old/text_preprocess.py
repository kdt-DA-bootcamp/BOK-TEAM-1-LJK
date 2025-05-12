import os
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
import inflect

# 필요한 NLTK 데이터 다운로드
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# 숫자 변환을 위한 객체
p = inflect.engine()

# 1️⃣ 전처리 함수
def preprocess_text(text):
    text = text.lower()  # 소문자 변환
    text = re.sub(r'[^\w\s]', '', text)  # 구두점 제거

    # 숫자와 단위가 결합된 형태 처리
    text = convert_numbers_with_units(text)

    # 숫자를 문자로 변환
    words = text.split()
    words = [convert_number(word) for word in words]  # 숫자 처리 함수 호출
    text = ' '.join(words)

    tokens = word_tokenize(text)  # 토큰화
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]  # 불용어 제거

    stemmer = PorterStemmer()
    lemmatizer = WordNetLemmatizer()

    stemmed_tokens = [stemmer.stem(word) for word in tokens]  # 어간추출
    lemmatized_tokens = [lemmatizer.lemmatize(word) for word in stemmed_tokens]  # 표제어추출

    return ' '.join(lemmatized_tokens)

# 숫자와 단위가 결합된 형태 처리 함수
def convert_numbers_with_units(text):
    # 숫자와 단위가 결합된 경우 (예: 40조원, 5000달러 등) 처리
    text = re.sub(r'(\d+)([^\d\s]+)', lambda x: p.number_to_words(x.group(1)) + ' ' + x.group(2), text)
    return text

# 숫자 변환 함수
def convert_number(word):
    try:
        # 숫자가 너무 클 경우 예외 처리
        if int(word) < 10**21:  # 10^21보다 작은 수만 변환
            return p.number_to_words(word)
        else:
            return word
    except ValueError:
        return word
    except inflect.NumOutOfRangeError:
        return word

# 2️⃣ 폴더 설정
input_folder = "text_output"  # 원본 텍스트 파일 폴더
output_folder = "토큰화2"  # 전처리된 파일 저장 폴더

# 출력 폴더 없으면 생성
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 3️⃣ 폴더 내 모든 txt 파일 처리
for filename in os.listdir(input_folder):
    if filename.endswith(".txt"):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        try:
            with open(input_path, "r", encoding="utf-8-sig") as file:
                text = file.read()

            processed_text = preprocess_text(text)

            with open(output_path, "w", encoding="utf-8-sig") as file:
                file.write(processed_text)

            print(f"✅ {filename} → 전처리 완료 후 저장됨!")
        except Exception as e:
            print(f"❌ {filename} 처리 중 오류 발생: {e}")

