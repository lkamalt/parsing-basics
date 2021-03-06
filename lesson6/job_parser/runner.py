from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from job_parser import settings
from job_parser.spiders.hhru import HhruSpider
from job_parser.spiders.sjru import SjruSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(HhruSpider)
    # process.crawl(SjruSpider)

    process.start()
