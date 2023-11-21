# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class GeneralItem(scrapy.Item):
    id = scrapy.Field()
    country = scrapy.Field()
    headquarter = scrapy.Field()
    operator = scrapy.Field()
    operator_wiki_url = scrapy.Field()
    company_name = scrapy.Field()
    founded = scrapy.Field()
    industry = scrapy.Field()
    sector = scrapy.Field()
    product = scrapy.Field()
    official_website = scrapy.Field()
    page_last_edit_date = scrapy.Field()
    facebook =scrapy.Field()
    twitter = scrapy.Field()
    linkedin = scrapy.Field()
    youtube = scrapy.Field()
    instagram = scrapy.Field()
    tiktok = scrapy.Field()
    numbers = scrapy.Field()
    emails = scrapy.Field()