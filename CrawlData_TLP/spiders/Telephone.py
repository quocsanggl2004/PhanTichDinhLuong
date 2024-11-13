import scrapy
import json
import re  
from scrapy.utils.reactor import install_reactor
from bs4 import BeautifulSoup
from kafka import KafkaProducer

install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')

class CellphonesGraphQLSpider(scrapy.Spider):
    name = "Telephone"
    allowed_domains = ["api.cellphones.com.vn"]
    start_urls = ['https://api.cellphones.com.vn/v2/graphql/query']

    def __init__(self, *args, **kwargs):
        super(CellphonesGraphQLSpider, self).__init__(*args, **kwargs)

        # Khởi tạo Kafka producer
        self.producer = KafkaProducer(
            bootstrap_servers='localhost:9094',  # Địa chỉ Kafka
            value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Chuyển đổi dữ liệu thành JSON
        )
        self.topic = 'webdata'  # Thay đổi tên topic

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

            # Xử lý giá
            price = filterable_info.get('price', 0)
            special_price = filterable_info.get('special_price', 0)
                
            product_data = {
                'product_id': general_info.get('product_id'),
                'name': name, 
                'price': price,
                'special_price': special_price,
                'total_count': general_info.get('review', {}).get('total_count'),
                'manufacturer': clean_text(general_info.get('manufacturer', 'N/A')),
                'operating_system': clean_text(attributes.get('operating_system', 'N/A')),
                'os_version': clean_text(attributes.get('os_version', 'N/A')),
                'battery': clean_text(attributes.get('battery', 'N/A')),
                'chipset': clean_text(attributes.get('chipset', 'N/A')),
                'display_size': clean_text(attributes.get('display_size', 'N/A')),
                'display_resolution': clean_text(attributes.get('display_resolution', 'N/A')),
                'mobile_type_of_display': clean_text(attributes.get('mobile_type_of_display', 'N/A')),
                'memory_internal': clean_text(attributes.get('memory_internal', 'N/A')),
                'storage': clean_text(attributes.get('storage', 'N/A')),
                'product_weight': clean_text(attributes.get('product_weight', 'N/A')),
                'mobile_tan_so_quet': clean_text(attributes.get('mobile_tan_so_quet', 'N/A')),
                'loai_mang': clean_text(attributes.get('loai_mang', 'N/A')),
                'mobile_cong_sac': clean_text(attributes.get('mobile_cong_sac', 'N/A')),
                'mobile_cam_bien_van_tay': clean_text(attributes.get('mobile_cam_bien_van_tay', 'N/A')),
                'warranty_information': clean_text(attributes.get('warranty_information', 'N/A')),
                'average_rating': average_rating,
                'key_selling_points': clean_html(attributes.get('key_selling_points', 'N/A')),
                'promotion_information': clean_html(filterable_info.get('promotion_information', 'N/A')),
            }

            # Ghi dữ liệu vào Kafka
            try:
                self.producer.send(self.topic, product_data)
                self.producer.flush()  # Đảm bảo rằng tin nhắn đã được gửi
                self.log(f'Sent data to Kafka: {product_data}')  # Log thông tin đã gửi
            except Exception as e:
                self.log(f"Error sending data to Kafka: {e}")

            yield product_data  # Tiếp tục trả về dữ liệu cho Scrapy

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

    def close(self, reason):
        # Đóng producer khi spider hoàn thành
        self.producer.close()