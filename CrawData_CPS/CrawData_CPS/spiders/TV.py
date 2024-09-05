import scrapy


class TvSpider(scrapy.Spider):
    name = "TV"
    allowed_domains = ["cellphones.com.vn"]
    start_urls = ["https://cellphones.com.vn/tivi.html"]


    def parse(self, response):
        # Duyệt qua từng sản phẩm trong danh mục
        for product in response.css('div.product-info-container'):
            yield {
                'product_name': product.css('h3::text').get(),
                'price_sale': product.css('p.product__price--show::text').get(),
                'price': product.css('p.product__price--through::text').get(default='N/A'),
                'rate_average': product.css('div.product__box-rating span::text').get(default='N/A'),
            }

        # Tìm đường dẫn tới trang kế tiếp, nếu có, và tiếp tục thu thập
        next_page = response.css('li.page-item a.page-link::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
