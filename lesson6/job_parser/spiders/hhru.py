import scrapy
from scrapy.http import HtmlResponse
from job_parser.items import JobParserItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = [
        'https://kazan.hh.ru/search/vacancy?area=1&search_field=name&search_field=company_name&search_field=description&text=python',
        'https://kazan.hh.ru/search/vacancy?area=2&search_field=name&search_field=company_name&search_field=description&text=python'
    ]

    def parse(self, response: HtmlResponse):
        next_page = response.xpath('//a[@data-qa="pager-next"]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath('//a[@data-qa="vacancy-serp__vacancy-title"]/@href').getall()
        for link in links:
            yield response.follow(link, callback=self.parse_vacancy)

    def parse_vacancy(self, response: HtmlResponse):
        name = response.xpath('//h1//text()').get()
        link = response.url
        salary = response.xpath('//div[@data-qa="vacancy-salary"]//text()').getall()
        item = JobParserItem(name=name, link=link, salary=salary)
        yield item
