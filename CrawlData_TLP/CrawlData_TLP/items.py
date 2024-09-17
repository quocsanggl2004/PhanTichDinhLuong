# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawldataTlpItem(scrapy.Item):
    # define the fields for your item here like:
    product_id = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    special_price = scrapy.Field()
    battery = scrapy.Field()
    display_size = scrapy.Field() 
    mobile_tan_so_quet = scrapy.Field() 
    manufacturer = scrapy.Field()
    camera_primary = scrapy.Field()
    camera_secondary = scrapy.Field()
    mobile_tinh_nang_camera = scrapy.Field()
    chipset = scrapy.Field()
    mobile_tinh_nang_dac_biet = scrapy.Field() 
    mobile_cong_nghe_sac = scrapy.Field()
    mobile_cong_sac = scrapy.Field()
    warranty_information = scrapy.Field()
    average_rating = scrapy.Field()
