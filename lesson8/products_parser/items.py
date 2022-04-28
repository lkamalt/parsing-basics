# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst
from tools.str_processing import get_float_number


class ProductsParserItem(scrapy.Item):
    name = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(get_float_number))
    link = scrapy.Field(output_processor=TakeFirst())
    _id = scrapy.Field()
