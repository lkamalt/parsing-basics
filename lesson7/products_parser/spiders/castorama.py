import scrapy


class CastoramaSpider(scrapy.Spider):
    name = 'castorama'
    allowed_domains = ['castorama.ru']
    start_urls = ['http://castorama.ru/']

    def parse(self, response):
        pass
