import asyncio
import json
import os
from playwright.async_api import async_playwright

# 2018년 1월 ~ 2025년 2월
YEARS = list(range(2018,2026))
MONTHS = list(range(1, 3))

# 동시 크롤링 제한 (한 번에 5개씩)
MAX_CONCURRENT_CRAWLS = 5

# 데이터 저장 폴더 설정
OUTPUT_DIR = "mk_news_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def fetch_article_urls(year, month):
    start_date = f"{year}-{str(month).zfill(2)}-01"
    end_date = f"{year}-{str(month).zfill(2)}-31"
    search_url = f"https://www.mk.co.kr/search/news?word=금리&sort=asc&dateType=direct&startDate={start_date}&endDate={end_date}&searchField=all&includeWord=금리&newsType=all"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  
        # headless 모드로 실행 (빠르게 크롤링)
        context = await browser.new_context()
        page = await context.new_page()

        print(f"\n🔍 [STEP 1] {year}-{month} 검색 페이지 열기: {search_url}")
        await page.goto(search_url)
        await page.wait_for_load_state("domcontentloaded")

        # 더보기 버튼 클릭
        while True:
            try:
                more_button = await page.query_selector("button[data-btn-more][data-append-selector='#list_area']")
                if more_button:
                    print(f"🔄 {year}-{month}: '더보기' 버튼 클릭")
                    await more_button.click()
                    await asyncio.sleep(3)  
                    # 클릭 후 로딩 대기
                    await page.wait_for_load_state("domcontentloaded")
                else:
                    print(f"{year}-{month}: '더보기' 버튼 없음. URL 수집 완료!")
                    break
            except Exception as e:
                print(f"{year}-{month}: '더보기' 버튼 클릭 오류: {e}")
                break

        # 기사 URL 크롤링
        articles = await page.query_selector_all("ul.news_list li.news_node a")
        article_urls = list(set([await article.get_attribute("href") for article in articles]))

        print(f"\n[{year}-{month}] 총 {len(article_urls)}개의 기사 URL 발견!")

        await browser.close()
        return article_urls


async def scrape_article(semaphore, context, url):
    """기사 본문을 크롤링 (제목에 '스탁론'이 포함된 기사는 제외)"""
    async with semaphore:  # 동시 크롤링 개수 제한
        page = await context.new_page()
        print(f"\n🔍 [START] 기사 크롤링: {url}")

        try:
            await page.goto(url, timeout=15000)
            await page.wait_for_load_state("domcontentloaded")

            # 제목 크롤링
            title_element = await page.query_selector("h2.news_ttl")
            title = await title_element.text_content() if title_element else "제목 없음"

            # 제목 필터링 (스탁론 포함 기사 제외)
            if "스탁론" in title:
                print(f"⚠️ [제외] 제목 '{title}' (스탁론 포함 기사)")
                await page.close()
                return None

            # 날짜 크롤링
            date_element = await page.query_selector("div.time_area dl dd")
            date = await date_element.text_content() if date_element else "날짜 없음"

            # 본문 크롤링
            try:
                content = await page.inner_text("div.news_cnt_detail_wrap", timeout=5000)
            except:
                content = "본문 없음"

            print(f"📰 제목: {title}")
            print(f"🗓 날짜: {date}")
            print(f"📝 본문 미리보기: {content[:200]}...")

        except Exception as e:
            print(f"[ERROR] {url} 크롤링 실패: {e}")
            return None

        await page.close()
        return {"title": title, "date": date, "content": content, "url": url}


async def process_month(year, month):
    """한 달 단위로 기사 URL을 수집하고 크롤링 (브라우저 유지 & 동시 크롤링 제한)"""
    article_urls = await fetch_article_urls(year, month)
    if not article_urls:
        print(f"[{year}-{month}] 크롤링할 기사 없음. 건너뜀!")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  
        # 속도 최적화
        context = await browser.new_context()
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_CRAWLS)  # 동시 크롤링 개수 제한

        # 기사 크롤링을 병렬로 실행 (최대 동시 5개)
        tasks = [scrape_article(semaphore, context, url) for url in article_urls]
        articles_data = await asyncio.gather(*tasks)

        await browser.close()

    # "스탁론"이 포함된 기사 제외 후 JSON 저장
    filtered_articles = [article for article in articles_data if article]

    json_filename = f"{OUTPUT_DIR}/mk_news_{year}_{str(month).zfill(2)}.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(filtered_articles, f, ensure_ascii=False, indent=4)

    print(f"\n🎉 [{year}-{month}] 크롤링 완료! (총 {len(filtered_articles)}개 기사)")
    print(f"💾 '{json_filename}' 저장 완료!")


async def main():
    """전체 기간을 한 달씩 나누어 크롤링"""
    for year in YEARS:
        for month in MONTHS:
            print(f"\n🚀 {year}-{month} 크롤링 시작...")
            await process_month(year, month)
            await asyncio.sleep(2)  # 크롤링 간격 추가 (서버 부담 방지)

asyncio.run(main())
