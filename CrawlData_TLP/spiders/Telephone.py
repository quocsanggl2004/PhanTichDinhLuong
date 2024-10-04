import scrapy
import json
import re  
from scrapy.utils.reactor import install_reactor
from bs4 import BeautifulSoup

install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')

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
                            filter_price: {from:0 to:54990000}
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
        if response.status != 200:
            self.log(f"Yêu cầu không thành công với mã trạng thái: {response.status}")
            return
        
        data = json.loads(response.text) 
        products = data.get('data', {}).get('products', [])

        if products is None:
            self.log("Không tìm thấy sản phẩm nào.")
            return  # Dừng lại nếu không có sản phẩm

        # Hàm loại bỏ các thẻ HTML
        def clean_html(text):
            if text:
                soup = BeautifulSoup(text, 'html.parser')
                return soup.get_text(strip=True)  # Trả về nội dung văn bản đã được làm sạch
            return 'N/A'

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
        
            # Định dạng average_rating
            average_rating = general_info.get('review', {}).get('average_rating')
            formatted_rating = f"{average_rating}/5" if average_rating else 'N/A'

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
                'mobile_ra_mat': clean_text(attributes.get('mobile_ra_mat', 'N/A')),
                'price': price,
                'special_price': special_price,
                'manufacturer': clean_text(general_info.get('manufacturer', 'N/A')),
                'operating_system': clean_text(attributes.get('operating_system', 'N/A')),
                'os_version': clean_text(attributes.get('os_version', 'N/A')),
                'battery': clean_text(attributes.get('battery', 'N/A')),
                'chipset': clean_text(attributes.get('chipset', 'N/A')),
                'display_size': clean_text(attributes.get('display_size', 'N/A')),
                'display_resolution': clean_text(attributes.get('display_resolution', 'N/A')),
                'mobile_type_of_display': clean_text(attributes.get('mobile_type_of_display', 'N/A')),
                'camera_primary': clean_html(attributes.get('camera_primary', 'N/A')),  # Sử dụng clean_html
                'camera_secondary': clean_html(attributes.get('camera_secondary', 'N/A')),  # Sử dụng clean_html
                'camera_video': clean_html(attributes.get('camera_video', 'N/A')),  # Sử dụng clean_html
                'memory_internal': clean_text(attributes.get('memory_internal', 'N/A')),
                'storage': clean_text(attributes.get('storage', 'N/A')),
                'product_weight': clean_text(attributes.get('product_weight', 'N/A')),
                'mobile_tan_so_quet': clean_text(attributes.get('mobile_tan_so_quet', 'N/A')),
                'mobile_jack_tai_nghe': clean_text(attributes.get('mobile_jack_tai_nghe', 'N/A')),
                'loai_mang': clean_text(attributes.get('loai_mang', 'N/A')),
                'mobile_cong_sac': clean_text(attributes.get('mobile_cong_sac', 'N/A')),
                'mobile_cam_bien_van_tay': clean_text(attributes.get('mobile_cam_bien_van_tay', 'N/A')),
                'warranty_information': clean_text(attributes.get('warranty_information', 'N/A')),
                'total_count': general_info.get('review', {}).get('total_count'),
                'average_rating': formatted_rating,  
                'mobile_display_features': clean_html(attributes.get('mobile_display_features', 'N/A')),  # Sử dụng clean_html
                'key_selling_points': clean_html(attributes.get('key_selling_points', 'N/A')),  # Sử dụng clean_html
                'promotion_information': clean_html(filterable_info.get('promotion_information', 'N/A')),  # Sử dụng clean_html
                'change_layout_preorder': clean_text(attributes.get('change_layout_preorder', 'N/A')),
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
                                filter_price: {from:0 to:54990000}
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
