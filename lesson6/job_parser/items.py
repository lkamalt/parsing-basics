# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobParserItem(scrapy.Item):
    name = scrapy.Field()
    salary = scrapy.Field()
    link = scrapy.Field()
    min_salary = scrapy.Field()
    max_salary = scrapy.Field()
    cur = scrapy.Field()
    _id = scrapy.Field()
