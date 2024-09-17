import scrapy
import json

class CellphonesGraphQLSpider(scrapy.Spider):
    name = "Telephone"
    allowed_domains = ["api.cellphones.com.vn"]
    start_urls = ['https://api.cellphones.com.vn/v2/graphql/query']

    def start_requests(self):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
        }

        # Payload cho trang đầu tiên (page 1)
        payload = {
            "query": """
            query GetProductsByCateId{
                products(
                    filter: {
                        static: {
                            categories: ["3"],
                            province_id: 30, 
                            stock: {from: 0},
                            stock_available_id: [46, 56, 152, 4164],
                            filter_price: {from:0to:54990000}
                        },
                        dynamic: {}
                    },
                    page: 1,
                    size: 20,
                    sort: [{view: desc}]
                ){
                    general{
                        product_id
                        name
                        attributes
                        sku
                        manufacturer
                        url_key
                        url_path
                        review{
                            total_count
                            average_rating
                        }
                    }
                    filterable{
                        price
                        special_price
                        promotion_information
                        thumbnail
                        promotion_pack
                    }
                }
            }""",
            "variables": {}
        }

        # Gửi yêu cầu POST đến API GraphQL cho trang 1
        yield scrapy.Request(
            url=self.start_urls[0],
            method="POST",
            headers=headers,
            body=json.dumps(payload),
            callback=self.parse_products,
            meta={'page': 1}
        )

    def parse_products(self, response):
        data = json.loads(response.text)
        products = data.get('data', {}).get('products', [])

        # Lưu từng sản phẩm
        for product in products:
            general_info = product.get('general', {})
            filterable_info = product.get('filterable', {})

            yield {
                'product_id': general_info.get('product_id'),
                'name': general_info.get('name'),
                'attributes': general_info.get('attributes'),
                'sku': general_info.get('sku'),
                'manufacturer': general_info.get('manufacturer'),
                'price': filterable_info.get('price'),
                'special_price': filterable_info.get('special_price'),
                'promotion': filterable_info.get('promotion_information'),
                'thumbnail': filterable_info.get('thumbnail'),
                'review_count': general_info.get('review', {}).get('total_count'),
                'average_rating': general_info.get('review', {}).get('average_rating'),
            }

        # Chuyển sang trang tiếp theo nếu còn sản phẩm
        current_page = response.meta.get('page')
        if products:  # Nếu còn sản phẩm trong trang hiện tại
            next_page = current_page + 1

            # Cập nhật payload cho trang tiếp theo
            next_payload = {
                "query": """
                query GetProductsByCateId{
                    products(
                        filter: {
                            static: {
                                categories: ["3"],
                                province_id: 30, 
                                stock: {from: 0},
                                stock_available_id: [46, 56, 152, 4164],
                                filter_price: {from:0to:54990000}
                            },
                            dynamic: {}
                        },
                        page: """ + str(next_page) + """,
                        size: 20,
                        sort: [{view: desc}]
                    ){
                        general{
                            product_id
                            name
                            attributes
                            sku
                            manufacturer
                            url_key
                            url_path
                            review{
                                total_count
                                average_rating
                            }
                        }
                        filterable{
                            price
                            special_price
                            promotion_information
                            thumbnail
                            promotion_pack
                        }
                    }
                }""",
                "variables": {}
            }

            # Gửi yêu cầu cho trang tiếp theo
            yield scrapy.Request(
                url=self.start_urls[0],
                method="POST",
                headers=response.request.headers,
                body=json.dumps(next_payload),
                callback=self.parse_products,
                meta={'page': next_page}
            )

    def parse(self, response):
        pass  # Không sử dụng phương thức này, nhưng Scrapy yêu cầu phải có.


    # def parse_product_details(self, response):
    #     item = response.meta['item']

    #     # Get the number of stars from rating elements
    #     rating_elements = response.css('div.box-rating .icon.is-active')
    #     star_count = len(rating_elements)

    #     # Get the number of reviews
    #     rating_text = response.css('div.box-rating::text').re_first(r'(\d+) đánh giá')

    #     if rating_text:
    #         item['rating_count'] = int(rating_text)
    #         item['rate_average'] = f"{star_count}/5"  # Hiển thị trung bình sao
    #     else:
    #         item['rating_count'] = 'null'
    #         item['rate_average'] = 'null'

    #     # Get outstanding features
    #     outstanding_feature_elements = response.css('div.ksp-content ul li::text').getall()
    #     item['outstanding_feature'] = ' | '.join(outstanding_feature_elements) if outstanding_feature_elements else 'N/A'

    #     # Print product details
    #     self.log(f"Product Details: {item}")

    #     yield item


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
