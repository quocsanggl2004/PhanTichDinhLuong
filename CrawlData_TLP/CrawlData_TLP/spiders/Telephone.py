import scrapy
import json
import re  

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

        # Hàm loại bỏ các thẻ HTML
        def remove_html_tags(text):
            clean = re.compile('<.*?>')
            return re.sub(clean, ' ', text)


        # Hàm xử lý văn bản
        def clean_text(text):
            if text:
                text = text.strip()  # Loại bỏ khoảng trắng đầu và cuối
                text = re.sub(r'\s+', ' ', text)  # Loại bỏ khoảng trắng thừa giữa các từ
            return text
        

        # Lưu từng sản phẩm
        for product in products:
            general_info = product.get('general', {})
            filterable_info = product.get('filterable', {})
            attributes = general_info.get('attributes', {})
        
            name = clean_text(general_info.get('name', 'N/A'))
        
            mobile_tinh_nang_camera_raw = attributes.get('mobile_tinh_nang_camera', 'N/A')
            mobile_tinh_nang_camera = clean_text(remove_html_tags(mobile_tinh_nang_camera_raw))
        
            mobile_cong_nghe_sac_raw = attributes.get('mobile_cong_nghe_sac', 'N/A')
            mobile_cong_nghe_sac = clean_text(remove_html_tags(mobile_cong_nghe_sac_raw))
        
            # Định dạng average_rating
            average_rating = general_info.get('review', {}).get('average_rating')
            if average_rating:
                formatted_rating = f"{average_rating}/5"
            else:
                formatted_rating = 'N/A'
        
            # Định dạng camera_primary và camera_secondary
            camera_primary = remove_html_tags(attributes.get('camera_primary', 'N/A'))
            camera_secondary = remove_html_tags(attributes.get('camera_secondary', 'N/A'))

            # Xử lý giá
            price = filterable_info.get('price', 0)
            special_price = filterable_info.get('special_price', 0)
            
            # Kiểm tra nếu cả price và special_price bằng 0 hoặc là None
            if (not price or price == 0) and (not special_price or special_price == 0):
                price = "Giá Liên Hệ"
                special_price = "Giá Liên Hệ"
        
            yield {
                'product_id': general_info.get('product_id'),
                'name': name, 
                'price': price,
                'special_price': special_price,
                'battery': clean_text(attributes.get('battery', 'N/A')),
                'display_size': clean_text(attributes.get('display_size', 'N/A')),
                'mobile_tan_so_quet': clean_text(attributes.get('mobile_tan_so_quet', 'N/A')),
                'manufacturer': clean_text(general_info.get('manufacturer', 'N/A')),
                'camera_primary': camera_primary,  
                'camera_secondary': camera_secondary,  
                'mobile_tinh_nang_camera': mobile_tinh_nang_camera,  
                'chipset': clean_text(attributes.get('chipset', 'N/A')),
                'mobile_tinh_nang_dac_biet': clean_text(attributes.get('mobile_tinh_nang_dac_biet', 'N/A')),
                'mobile_cong_nghe_sac': mobile_cong_nghe_sac,  
                'mobile_cong_sac': clean_text(attributes.get('mobile_cong_sac', 'N/A')),
                'warranty_information': clean_text(attributes.get('warranty_information', 'N/A')),
                'average_rating': formatted_rating,  
            }

        # Chuyển sang trang tiếp theo nếu còn sản phẩm
        current_page = response.meta.get('page')
        if products:
            next_page = current_page + 1

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

            yield scrapy.Request(
                url=self.start_urls[0],
                method="POST",
                headers=response.request.headers,
                body=json.dumps(next_payload),
                callback=self.parse_products,
                meta={'page': next_page}
            )


    def parse(self, response):
        pass  


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


    # def extract_promotion_text(self, product):
    #     parts = product.css('div.promotion p::text').getall()
    #     promotion_text = ' '.join(part.strip() for part in parts)
    #     return promotion_text

    # def clean_text(self, text):
    #     if text:
    #         text = text.replace('\xa0', ' ')
    #         return ' '.join(text.split())
    #     return text

    # def close(self, reason):
    #     # Đóng trình điều khiển Selenium khi kết thúc
    #     self.driver.quit()
