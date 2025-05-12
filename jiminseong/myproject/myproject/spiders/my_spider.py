import scrapy
import re
import os
import fitz  # PyMuPDF
from datetime import datetime
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor

class DebentureSpider(scrapy.Spider):
    name = "debenture"
    allowed_domains = ["finance.naver.com", "stock.pstatic.net"]

    start_urls = [
        'https://finance.naver.com/research/debenture_list.naver?keyword=&brokerCode=&searchType=writeDate&writeFromDate=2008-01-01&writeToDate=2025-11-30&x=32&y=22&page=1'
    ]

    def __init__(self):
        self.downloaded_pdfs = set()  # 중복 방지를 위한 세트
        self.executor = ThreadPoolExecutor(max_workers=5)  # 최대 5개 스레드를 사용

    def parse(self, response):
        # 페이지에서 데이터 추출
        rows = response.xpath('//table[@class="type_1"]/tr')
        date_pattern = re.compile(r'^\s*\d{2}\.\d{2}\.\d{2}\s*$')

        for row in rows:
            title = row.xpath('.//td[1]/a/text()').get()
            if not title:
                continue

            # PDF URL을 추출
            pdf_url = row.xpath('.//td[@class="file"]/a/@href').get()
            if pdf_url:
                pdf_url = response.urljoin(pdf_url)

                # 중복 체크
                if pdf_url in self.downloaded_pdfs:
                    continue
                self.downloaded_pdfs.add(pdf_url)  # 다운로드한 URL 기록

                # PDF 파일 다운로드
                yield scrapy.Request(pdf_url, callback=self.save_pdf, meta={'title': title.strip()}, dont_filter=True)

            date_str = row.xpath('.//td[4]/text()').get()
            if not date_str or not date_pattern.match(date_str.strip()):
                continue

            try:
                date_obj = datetime.strptime(date_str.strip(), '%y.%m.%d')
                formatted_date = date_obj.strftime('%Y-%m-%d')
            except Exception:
                formatted_date = date_str.strip()

            yield {
                'title': title.strip(),
                'pdf_url': pdf_url,
                'date': formatted_date,
            }

        # 페이지네이션 처리
        current_page = int(response.url.split("page=")[-1])
        if current_page < 284:
            next_page = current_page + 1
            next_url = response.url.replace(f"page={current_page}", f"page={next_page}")
            yield scrapy.Request(next_url, callback=self.parse)

    def save_pdf(self, response):
        title = response.meta['title']
        pdf_name = f"{title}.pdf"

        output_dir = "downloaded_pdfs"
        os.makedirs(output_dir, exist_ok=True)

        pdf_path = os.path.join(output_dir, pdf_name)
        with open(pdf_path, 'wb') as f:
            f.write(response.body)

        # PDF 텍스트 추출을 멀티스레딩으로 처리
        self.executor.submit(self.extract_text_from_pdf, response.body, title)

    def extract_text_from_pdf(self, pdf_data, title):
        # PyMuPDF(fitz) 사용하여 PDF에서 텍스트 추출
        with BytesIO(pdf_data) as pdf_file:
            doc = fitz.open(pdf_file)  # PDF 파일 열기
            text = ''
            for page_num in range(doc.page_count):  # 모든 페이지 순회
                page = doc.load_page(page_num)  # 페이지 로드
                text += page.get_text("text")  # 텍스트 추출

        output_dir = "downloaded_pdfs"
        text_file_name = f"{title}.txt"
        with open(os.path.join(output_dir, text_file_name), 'w', encoding='utf-8') as text_file:
            text_file.write(text)

        self.logger.info(f"PDF에서 추출된 텍스트 저장 완료: {text_file_name}")
