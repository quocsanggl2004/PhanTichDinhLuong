import scrapy
from scrapy.http import HtmlResponse

class TvSpider(scrapy.Spider):
    name = "TV"
    allowed_domains = ["cellphones.com.vn"]
    start_urls = ["https://cellphones.com.vn/tivi.html"]

    def parse(self, response):
        products = response.css('div.product-info-container')
        
        for product in products:
            promotion_text = self.extract_promotion_text(product)
            yield {
                'product_name': self.clean_text(product.css('h3::text').get(default='N/A')),
                'price_sale': self.clean_text(product.css('p.product__price--show::text').get(default='N/A')),
                'price': self.clean_text(product.css('p.product__price--through::text').get(default='N/A')),
                'percent_discount': self.clean_text(product.css('p.product__price--percent-detail::text').get(default='N/A')),
                'promotion': promotion_text,
                'outstanding_feature': self.clean_text(product.css('div.outstanding-features::text').get(default='N/A')),
                'screen_size': self.clean_text(product.css('span.screen-size::text').get(default='N/A')),
                'rating_count': self.clean_text(product.css('span.rating-count::text').get(default='N/A')),
                'rate_average': self.clean_text(product.css('span.rate-average::text').get(default='N/A')),
                'comment': self.clean_text(product.css('div.comment-section p::text').get(default='N/A'))
            }

        next_page = response.css('a.next-page::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)

        load_more_button = response.css('a.button__show-more-product::attr(href)').get()
        if load_more_button:
            yield response.follow(load_more_button, self.parse)

    def extract_promotion_text(self, product):
        # Kết hợp nội dung từ nhiều phần tử
        parts = product.css('div.promotion p::text').getall()
        # Kết hợp các phần lại với nhau, loại bỏ các ký tự thừa
        promotion_text = ' '.join(part.strip() for part in parts)
        return promotion_text

    def clean_text(self, text):
        if text:
            # Chuyển đổi ký tự Unicode escape về dạng ký tự
            text = text.replace('\xa0', ' ')
            return ' '.join(text.split())
        return text
