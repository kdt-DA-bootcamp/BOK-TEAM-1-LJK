import scrapy
import re
import os
from datetime import datetime

class DebentureSpider(scrapy.Spider):
    name = "debenture"
    allowed_domains = ["finance.naver.com", "stock.pstatic.net"]

    start_urls = [
        'https://finance.naver.com/research/debenture_list.naver?keyword=&brokerCode=&searchType=writeDate&writeFromDate=2008-01-01&writeToDate=2025-11-30&x=32&y=22&page=1'
    ]

    def __init__(self):
        self.downloaded_pdfs = set()  # 중복 방지를 위한 세트

    def parse(self, response):
        rows = response.xpath('//table[@class="type_1"]/tr')
        
        date_pattern = re.compile(r'^\s*\d{2}\.\d{2}\.\d{2}\s*$')
        
        for row in rows:
            # 제목
            title = row.xpath('.//td[1]/a/text()').get()
            if not title:
                continue
            
            # PDF 링크
            pdf_url = row.xpath('.//td[@class="file"]/a/@href').get()
            if pdf_url:
                pdf_url = response.urljoin(pdf_url)  # 절대 URL로 변환
                
                # 중복 체크
                if pdf_url in self.downloaded_pdfs:
                    self.logger.info(f"이미 다운로드한 PDF: {title.strip()}")
                    continue
                self.downloaded_pdfs.add(pdf_url)  # 다운로드한 URL 기록

                # PDF 파일 다운로드
                yield scrapy.Request(pdf_url, callback=self.save_pdf, meta={'title': title.strip()})
            
            # 날짜 (예: '24.11.29')
            date_str = row.xpath('.//td[4]/text()').get()
            if not date_str or not date_pattern.match(date_str.strip()):
                continue
            
            # 날짜 형식 변환
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
            self.logger.info(f"다음 페이지 크롤링: {next_page}")
            yield scrapy.Request(next_url, callback=self.parse)

    def save_pdf(self, response):
        # PDF 파일 저장
        title = response.meta['title']
        pdf_name = f"{title}.pdf"
        
        # 파일 저장 경로 설정
        output_dir = "downloaded_pdfs"
        os.makedirs(output_dir, exist_ok=True)
        
        # PDF 파일 저장
        with open(os.path.join(output_dir, pdf_name), 'wb') as f:
            f.write(response.body)
        
        self.logger.info(f"PDF 파일 다운로드 완료: {pdf_name}")
