from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

from basic_info.spiders.official_and_social_spider import OperatorWikiSpider

process = CrawlerProcess()
process.crawl(OperatorWikiSpider)

process.start()
