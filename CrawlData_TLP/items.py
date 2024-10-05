# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawldataTlpItem(scrapy.Item):
    # define the fields for your item here like:
    product_id = scrapy.Field()
    name = scrapy.Field()
    mobile_ra_mat = scrapy.Field()
    price = scrapy.Field()
    special_price = scrapy.Field()
    manufacturer = scrapy.Field()
    operating_system = scrapy.Field()
    os_version = scrapy.Field()
    battery = scrapy.Field()
    chipset = scrapy.Field()
    display_size = scrapy.Field()
    display_resolution = scrapy.Field()
    mobile_type_of_display = scrapy.Field()
    camera_primary = scrapy.Field()
    camera_secondary = scrapy.Field()
    camera_video = scrapy.Field()
    memory_internal = scrapy.Field()
    storage = scrapy.Field()
    product_weight = scrapy.Field()
    mobile_tan_so_quet = scrapy.Field()
    loai_mang = scrapy.Field()
    mobile_cong_sac = scrapy.Field()
    mobile_cam_bien_van_tay = scrapy.Field()
    warranty_information = scrapy.Field()
    total_count = scrapy.Field()
    average_rating = scrapy.Field()
    key_selling_points = scrapy.Field()
    promotion_information = scrapy.Field()



