# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AptekaItem(scrapy.Item):
    timestamp = scrapy.Field()
    RPC = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    marketing_tags = scrapy.Field()
    brand = scrapy.Field()
    section = scrapy.Field()
    price = scrapy.Field()
    in_stock = scrapy.Field()
    main_image = scrapy.Field()
    description = scrapy.Field()
    location = scrapy.Field()
    variants = scrapy.Field()

