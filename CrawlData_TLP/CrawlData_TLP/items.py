# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawldataTlpItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    product_id = scrapy.Field()
    name = scrapy.Field()
    attributes = scrapy.Field()
    sku = scrapy.Field()
    manufacturer = scrapy.Field()
    price = scrapy.Field()
    special_price = scrapy.Field()  
    promotion = scrapy.Field() 
    thumbnail = scrapy.Field()  
    review_count = scrapy.Field()
    average_rating = scrapy.Field()  
