import scrapy
from datetime import datetime

class EdailySpider(scrapy.Spider):
    name = "edaily"
    allowed_domains = ["edaily.co.kr"]

    start_urls = [
        'https://www.edaily.co.kr/search/news/?source=total&keyword=금리&exclude=&jname=&start=20250101&end=20251231&page=1'
    ]

    def parse(self, response):
        articles = response.css('.newsbox_04')

        for article in articles:
            # 기사 제목
            title = article.css("a::attr(title)").get()
            
            # 기사 내용
            contents_list = article.css(".newsbox_texts li::text").getall()
            contents = " ".join(text.strip() for text in contents_list).strip()

            # 날짜
            date_str = article.css(".author_category::text").get()
            date_obj = datetime.strptime(date_str.strip(), '%Y.%m.%d')
            formatted_date = date_obj.strftime("%Y-%m-%d")

            yield {
                'title' : title,
                'contents' : contents,
                'date' : formatted_date
            }

        current_page = int(response.url.split("page=")[-1])
        next_page = current_page + 1
        next_url = response.url.replace(f"page={current_page}", f"page={next_page}")

        yield scrapy.Request(url=next_url, callback=self.parse)