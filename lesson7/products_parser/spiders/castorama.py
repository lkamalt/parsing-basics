import scrapy
from scrapy.http import HtmlResponse
from products_parser.items import ProductsParserItem
from scrapy.loader import ItemLoader


class CastoramaSpider(scrapy.Spider):
    name = 'castorama'
    allowed_domains = ['castorama.ru']
    start_urls = ['https://www.castorama.ru/gardening-and-outdoor/garden-plants-and-seedlings']

    def parse(self, response: HtmlResponse):
        links = response.xpath('//a[@class="product-card__name ga-product-card-name"]/@href').getall()
        for link in links:
            yield response.follow(link, callback=self.parse_card)

    def parse_card(self, response: HtmlResponse):
        loader = ItemLoader(item=ProductsParserItem(), response=response)
        loader.add_xpath('name', '//h1/text()')
        loader.add_xpath('price', '//span[@class="price"]//text()')
        loader.add_value('link', response.url)
        loader.add_xpath('photos', '//img[contains(@class, "top-slide__img")]/@data-src')
        yield loader.load_item()
