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
        self.driver.get(response.url)
        time.sleep(3)
    
        # Continuously scroll and click "See More" button until all products are loaded
        while True:
            try:
                # Chờ nút "Xem thêm" xuất hiện và có thể nhấp
                load_more_button = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.button.btn-show-more.button__show-more-product'))
                )
                # Nhấn nút "Xem thêm"
                load_more_button.click()
                time.sleep(5)  # Tăng thời gian chờ để đảm bảo sản phẩm được tải
            except Exception as e:
                # Kiểm tra nếu nút không còn xuất hiện hoặc không thể nhấn (đã hết sản phẩm)
                self.log(f"No more products to load: {str(e)}")
                break
        
    
        # After all products are loaded, get the page source
        page_source = self.driver.page_source
        sel = Selector(text=page_source)
    
        # Process the products
        for product in sel.css('div.product-info'):
            product_url = product.css('a.product__link::attr(href)').get()
            product_id = product_url.split('/')[-1].replace('.html', '')
    
            # Log to check structure
            self.log(f"Product Badge HTML: {product.xpath('.//div[@class=\"product__badge"]').get()}")
    
            # Extract data using XPath
            screen_size = product.xpath('.//div[@class="product__badge"]/p[1]/text()').get(default='N/A')
            ram = product.xpath('.//div[@class="product__badge"]/p[2]/text()').get(default='N/A')
            rom = product.xpath('.//div[@class="product__badge"]/p[3]/text()').get(default='N/A')
    
            # Store in an item dictionary
            item = {
                'product_name': product.css('h3::text').get(),
                'price_sale': self.clean_text(product.css('p.product__price--show::text').get(default='N/A')),
                'price': self.clean_text(product.css('p.product__price--through::text').get(default='N/A')),
                'percent_discount': self.clean_text(product.css('p.product__price--percent-detail::text').get(default='N/A')),
                'promotion': self.extract_promotion_text(product),
                'screen_size': screen_size,
                'ram': ram,
                'rom': rom,
                'rating_count': self.clean_text(product.css('span.product__rating--count::text').get(default='N/A')),
                'rate_average': self.clean_text(product.css('span.product__rating--average::text').get(default='N/A')),
                'outstanding_feature': product.css('div.product__feature::text').get(default='N/A')
            }
    
            yield response.follow(product_url, self.parse_product_details, meta={'item': item})
    
            self.driver.get(response.url)
            time.sleep(3)
    
            # Cuộn xuống để đảm bảo tất cả dữ liệu được tải
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
    
            while True:
                try:
                    load_more_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.button.btn-show-more.button__show-more-product'))
                    )
                    load_more_button.click()
                    time.sleep(3)
                except Exception as e:
                    break
                
            page_source = self.driver.page_source
            sel = Selector(text=page_source)
    
            for product in sel.css('div.product-info'):
                product_url = product.css('a.product__link::attr(href)').get()
                product_id = product_url.split('/')[-1].replace('.html', '')
    
                self.log(f"Product HTML: {product.get()}")
    
                screen_size = product.xpath('.//div[@class="product__badge"]/p[1]/text()').get(default='N/A')
                ram = product.xpath('.//div[@class="product__badge"]/p[2]/text()').get(default='N/A')
                rom = product.xpath('.//div[@class="product__badge"]/p[3]/text()').get(default='N/A')
    
                item = {
                    'product_name': product.css('h3::text').get(),
                    'price_sale': self.clean_text(product.css('p.product__price--show::text').get(default='N/A')),
                    'price': self.clean_text(product.css('p.product__price--through::text').get(default='N/A')),
                    'percent_discount': self.clean_text(product.css('p.product__price--percent-detail::text').get(default='N/A')),
                    'promotion': self.extract_promotion_text(product),
                    'screen_size': screen_size,
                    'ram': ram,
                    'rom': rom,
                    'rating_count': self.clean_text(product.css('span.product__rating--count::text').get(default='N/A')),
                    'rate_average': self.clean_text(product.css('span.product__rating--average::text').get(default='N/A')),
                    'outstanding_feature': product.css('div.product__feature::text').get(default='N/A')
                }
    
                yield response.follow(product_url, self.parse_product_details, meta={'item': item})


    def parse_product_details(self, response):
        item = response.meta['item']

        # Get the number of stars from rating elements
        rating_elements = response.css('div.box-rating .icon.is-active')
        star_count = len(rating_elements)

        # Get the number of reviews
        rating_text = response.css('div.box-rating::text').re_first(r'(\d+) đánh giá')

        if rating_text:
            item['rating_count'] = int(rating_text)
            item['rate_average'] = f"{star_count}/5"  # Hiển thị trung bình sao
        else:
            item['rating_count'] = 'null'
            item['rate_average'] = 'null'

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