from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from products_parser import settings
from products_parser.spiders.castorama import CastoramaSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(CastoramaSpider)

    process.start()
