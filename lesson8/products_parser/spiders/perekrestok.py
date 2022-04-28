import scrapy
from scrapy.http import HtmlResponse
from products_parser.items import ProductsParserItem
from scrapy.loader import ItemLoader


class PerekrestokSpider(scrapy.Spider):
    name = 'perekrestok'
    allowed_domains = ['perekrestok.ru']
    start_urls = ['https://www.perekrestok.ru/cat/mc/187/sladosti-i-sneki']

    def parse(self, response):
        links = response.xpath('//a[contains(@class, "product-card__link")]/@href').getall()
        for link in links:
            yield response.follow(link, callback=self.parse_product)

    def parse_product(self, response: HtmlResponse):
        loader = ItemLoader(item=ProductsParserItem(), response=response)
        loader.add_xpath('name', '//h1/text()')
        loader.add_xpath('price', '//div[@class="price-new"]//text()')
        loader.add_value('link', response.url)
        yield loader.load_item()
