import os
import fitz  # PyMuPDF
from io import BytesIO

# PDF에서 텍스트 추출하는 함수
def extract_text_from_pdf(pdf_path):
    try:
        # PDF 파일 열기
        with open(pdf_path, 'rb') as file:
            doc = fitz.open(file)  # PyMuPDF로 PDF 파일 열기
            text = ''
            # 각 페이지에서 텍스트 추출
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                text += page.get_text("text")  # 텍스트 추출

        return text
    except Exception as e:
        print(f"PDF 텍스트 추출 실패: {e}")
        return None

# PDF 파일이 저장된 폴더 경로
pdf_dir = 'C:/Users/abwm2/Desktop/BootCamp/TIL/JIMINSEONG/jiminseong/myproject/downloaded_pdfs'

# 추출된 텍스트를 저장할 폴더 경로
output_dir = 'C:/Users/abwm2/Desktop/BootCamp/TIL/JIMINSEONG/jiminseong/myproject/text_output'
os.makedirs(output_dir, exist_ok=True)  # 폴더가 없으면 생성

# 폴더 내 모든 PDF 파일 처리
for filename in os.listdir(pdf_dir):
    if filename.endswith('.pdf'):  # PDF 파일만 처리
        pdf_path = os.path.join(pdf_dir, filename)  # 파일 경로 생성
        print(f"Processing PDF: {filename}")
        
        # PDF에서 텍스트 추출
        extracted_text = extract_text_from_pdf(pdf_path)
        
        if extracted_text:
            # 텍스트를 텍스트 파일로 저장
            text_filename = f"{filename[:-4]}.txt"  # PDF 파일 이름에서 확장자 .pdf 제거
            text_path = os.path.join(output_dir, text_filename)  # 저장 경로 생성

            with open(text_path, 'w', encoding='utf-8') as text_file:
                text_file.write(extracted_text)
            print(f"텍스트 파일 저장 완료: {text_filename}")
        else:
            print(f"텍스트 추출 실패: {filename}")
