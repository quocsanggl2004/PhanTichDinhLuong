import scrapy

class TVSpider(scrapy.Spider):
    name = "TV"
    allowed_domains = ["cellphones.com.vn"]
    start_urls = ["https://cellphones.com.vn/tivi.html"]

    def parse(self, response):
        # Lặp qua từng sản phẩm trong trang danh sách
        for product in response.css('div.product-info'):
            product_url = product.css('a.product__link::attr(href)').get()
            product_id = product_url.split('/')[-1].replace('.html', '')

            item = {
                'product_id': product_id,
                'product_name': product.css('h3::text').get(),
                'price_sale': self.clean_text(product.css('p.product__price--show::text').get(default='N/A')),
                'price': self.clean_text(product.css('p.product__price--through::text').get(default='N/A')),
                'percent_discount': self.clean_text(product.css('p.product__price--percent-detail::text').get(default='N/A')),
                'promotion': self.extract_promotion_text(product),
                'screen_size': product.css('h3::text').re(r'(\d{2} inch)')[0] if product.css('h3::text').re(r'(\d{2} inch)') else 'N/A',
                'rating_count': 'N/A',
                'rate_average': 'N/A',
                'comment': [],
            }

            # Follow the product URL to get detailed information
            yield response.follow(product_url, self.parse_product_details, meta={'item': item})

        # Phân trang
        next_page = response.css('a.next-page::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def parse_product_details(self, response):
        item = response.meta['item']

        # Lấy số lượng sao từ các phần tử đánh giá
        rating_elements = response.css('div.box-rating .icon.is-active')
        star_count = len(rating_elements)
        item['rate_average'] = star_count  # Đặt điểm đánh giá trung bình là số sao (sẽ cần cập nhật nếu cần điểm chính xác)

        # Lấy số lượng đánh giá
        rating_text = response.css('div.box-rating::text').re_first(r'(\d+) đánh giá')
        item['rating_count'] = int(rating_text) if rating_text else 'N/A'

        # Lấy bình luận
        item['comment'] = response.css('div.comment-content p::text').getall()  # Cập nhật selector phù hợp

        # In thông tin chi tiết sản phẩm ra màn hình
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
