import scrapy
from scrapy.http import HtmlResponse
from job_parser.items import JobParserItem


class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = [
        'https://www.superjob.ru/vacancy/search/?keywords=python&geo%5Br%5D%5B0%5D=3',
        'https://www.superjob.ru/vacancy/search/?keywords=python&geo%5Br%5D%5B0%5D=2',
    ]

    def parse(self, response: HtmlResponse):
        next_page = response.xpath('//a[contains(@class, "f-test-button-dalshe")]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath('//span[@class="-gENC _1TcZY Bbtm8"]//@href').getall()
        for link in links:
            yield response.follow(link, callback=self.parse_vacancy)

    def parse_vacancy(self, response: HtmlResponse):
        name = response.xpath('//h1//text()').getall()
        link = response.url
        salary = response.xpath('//span[@class="_2eYAG -gENC _1TcZY dAWx1"]//text()').getall()
        item = JobParserItem(name=name, link=link, salary=salary)
        yield item
