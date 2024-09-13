from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options  # Import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from scrapy import Selector
import scrapy


class TVSpider(scrapy.Spider):
    name = "Telephone"
    allowed_domains = ["cellphones.com.vn"]
    start_urls = ["https://cellphones.com.vn/mobile.html"]

    def __init__(self, *args, **kwargs):
        super(TVSpider, self).__init__(*args, **kwargs)
        
        # Cấu hình Selenium với Chrome
        chrome_options = Options()  
        chrome_options.add_argument("--headless")  # Chạy ở chế độ ẩn
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def parse(self, response):
        # Sử dụng Selenium để mở trang và bấm nút "Xem thêm"
        self.driver.get(response.url)
        time.sleep(3)  # Chờ trang tải

        # Nhấp vào nút "Xem thêm" cho đến khi tất cả sản phẩm được tải
        while True:
            try:
                # Sử dụng WebDriverWait để đợi nút "Xem thêm" xuất hiện
                load_more_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.button.btn-show-more.button__show-more-product'))
                )
                
                load_more_button.click()
                time.sleep(3) 
            except Exception as e:
                # Khi không còn nút "Xem thêm", thoát khỏi vòng lặp
                break

        # Lấy nội dung của trang sau khi tất cả sản phẩm đã tải
        page_source = self.driver.page_source
        sel = Selector(text=page_source)

        # Loop through each product on the listing page
        for product in sel.css('div.product-info'):
            product_url = product.css('a.product__link::attr(href)').get()
            product_id = product_url.split('/')[-1].replace('.html', '')

            item = {
                    'product_name': product.css('h3::text').get(),
                    'price_sale': self.clean_text(product.css('p.product__price--show::text').get(default='N/A')),
                    'price': self.clean_text(product.css('p.product__price--through::text').get(default='N/A')),
                    'percent_discount': self.clean_text(product.css('p.product__price--percent-detail::text').get(default='N/A')),
                    'promotion': self.extract_promotion_text(product),
                    'screen_size': product.css('div.product__badge p.product__more-info__item::text').re(r'(\d+\.\d+ inches)')[0] if product.css('div.product__badge p.product__more-info__item::text').re(r'(\d+\.\d+ inches)') else 'N/A',
                    'ram': product.css('div.product__badge p.product__more-info__item::text').re(r'(\d+ GB)')[0] if len(product.css('div.product__badge p.product__more-info__item::text').re(r'(\d+ GB)')) >= 1 else 'N/A',
                    'rom': product.css('div.product__badge p.product__more-info__item::text').re(r'(\d+ GB)')[1] if len(product.css('div.product__badge p.product__more-info__item::text').re(r'(\d+ GB)')) >= 2 else 'N/A',
                    'rating_count': self.clean_text(product.css('span.product__rating--count::text').get(default='N/A')),
                    'rate_average': self.clean_text(product.css('span.product__rating--average::text').get(default='N/A')),
                    'outstanding_feature': product.css('div.product__feature::text').get(default='N/A')
                    }

            # Follow the product URL to get detailed information
            yield response.follow(product_url, self.parse_product_details, meta={'item': item})

    def parse_product_details(self, response):
        item = response.meta['item']

        # Get the number of stars from rating elements
        rating_elements = response.css('div.box-rating .icon.is-active')
        star_count = len(rating_elements)

        # Lấy tổng số lượt đánh giá cho mỗi mức sao
        rating_counts = response.css('div.rating-breakdown li::text').re(r'(\d+) đánh giá (\d) sao')
        
        # Lấy tổng số lượt đánh giá
        total_reviews = response.css('div.box-rating::text').re_first(r'(\d+) đánh giá')
        total_reviews = int(total_reviews) if total_reviews else 0
        
        # Tính tổng số điểm
        total_score = sum(int(count) * int(star) for count, star in rating_counts) if rating_counts else 0
        
        # Tính trung bình điểm
        if total_reviews > 0:
            average_rating = total_score / total_reviews
        else:
            average_rating = 'null'
        
        item['rating_count'] = total_reviews
        item['rate_average'] = f"{average_rating:.1f}/5" if average_rating != 'null' else 'null'

        # Get outstanding features
        outstanding_feature_elements = response.css('div.ksp-content ul li::text').getall()
        item['outstanding_feature'] = ' | '.join(outstanding_feature_elements) if outstanding_feature_elements else 'N/A'

        # Print product details
        self.log(f"Product Details: {item}")

        yield item

    def extract_promotion_text(self, product):
        parts = product.css('div.promotion p::text').getall()
        promotion_text = ' '.join(part.strip() for part in parts)
        return promotion_text

    def clean_text(self, text):
        if text:
            text = text.replace('\xa0', ' ')
            return ' '.join(text.split())
        return text

    def close(self, reason):
        # Đóng trình điều khiển Selenium khi kết thúc
        self.driver.quit()