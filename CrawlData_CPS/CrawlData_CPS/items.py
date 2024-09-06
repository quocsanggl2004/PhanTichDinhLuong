# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawldataCpsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    product_name = scrapy.Field()
    price_sale = scrapy.Field()
    price = scrapy.Field()
    percent_discount = scrapy.Field()
    promotion = scrapy.Field()
    outstanding_feature = scrapy.Field()
    screen_size = scrapy.Field()  
    rating_count = scrapy.Field()  
    rate_average = scrapy.Field()
    comment = scrapy.Field()

