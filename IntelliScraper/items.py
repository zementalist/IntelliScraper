# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class IntelliscraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class WikilinkItem(scrapy.Item):
    company_name = scrapy.Field()
    founded = scrapy.Field()
    industry = scrapy.Field()
    product = scrapy.Field()
    official_website = scrapy.Field()
    page_last_edit_date = scrapy.Field()