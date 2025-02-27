import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pdfplumber

# 다운로드 폴더 설정
download_folder = "BOK_Minutes2"
os.makedirs(download_folder, exist_ok=True)

# Selenium WebDriver 설정
chrome_options = Options()
chrome_options.add_argument("--headless")  # 브라우저 창 없이 실행
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# 한국은행 금융통화위원회 의사록 페이지 URL
base_url = "https://www.bok.or.kr/portal/singl/newsData/list.do?pageIndex={}&targetDepth=3&menuNo=201154&syncMenuChekKey=1&depthSubMain=&subMainAt=&searchCnd=1&searchKwd=&depth2=200038&depth3=201154&depth4=200789&date=&sdate=&edate=&sort=1&pageUnit=10"

# 페이지 크롤링 시작
for page_index in range(1, 14):  # 1페이지부터 13페이지까지
    print(f"크롤링 중: 페이지 {page_index}")  # 현재 페이지 출력
    page_url = base_url.format(page_index)  # pageIndex를 포함한 URL 생성
    driver.get(page_url)
    time.sleep(3)  # 페이지 로딩 대기

    # BeautifulSoup으로 페이지 HTML 분석
    soup = BeautifulSoup(driver.page_source, "html.parser")
    articles = soup.select("#bbsList > div.bd-line > ul > li > div > a")  # 수정된 선택자 사용

    if not articles:
        print("더 이상 항목이 없습니다.")
        continue  # 다음 페이지로 넘어감

    for article in articles:
        article_url = "https://www.bok.or.kr" + article["href"]
        driver.get(article_url)
        time.sleep(2)

        # 첨부파일 링크 추출
        article_soup = BeautifulSoup(driver.page_source, "html.parser")
        attachments = article_soup.select("#board > div > div.down-set a")  # 수정된 선택자 사용

        if not attachments:
            print("첨부파일이 없습니다.")
        else:
            for attachment in attachments:
                file_url = "https://www.bok.or.kr" + attachment["href"]
                file_name = attachment.text.strip()
                file_path = os.path.join(download_folder, file_name)

                # 파일 이름 중복 처리
                if os.path.exists(file_path):
                    base_name, extension = os.path.splitext(file_name)
                    counter = 1
                    while os.path.exists(file_path):
                        file_path = os.path.join(download_folder, f"{base_name}_{counter}{extension}")
                        counter += 1

                # 파일 다운로드
                response = requests.get(file_url, stream=True)
                if response.status_code == 200:  # 다운로드 성공 여부 확인
                    with open(file_path, "wb") as file:
                        for chunk in response.iter_content(chunk_size=1024):
                            if chunk:
                                file.write(chunk)
                    print(f"다운로드 완료: {file_path}")

                    # PDF 파일의 텍스트 추출
                    if file_name.lower().endswith(".pdf"):
                        with pdfplumber.open(file_path) as pdf:
                            text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
                        text_file_path = file_path.replace(".pdf", ".txt")
                        with open(text_file_path, "w", encoding="utf-8") as text_file:
                            text_file.write(text)
                        print(f"텍스트 추출 완료: {text_file_path}")
                else:
                    print(f"파일 다운로드 실패: {file_name}")

        # 이전 페이지로 돌아가기
        driver.back()
        time.sleep(2)

# 브라우저 종료
driver.quit()
