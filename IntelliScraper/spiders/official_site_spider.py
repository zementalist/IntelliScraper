import scrapy
from ..items import SocialMediaLinksItem
from scrapy.http import HtmlResponse
from ..helper import *
import re


class OfficialSiteSpider(scrapy.Spider):
    name = 'official_site'

    def __init__(self):
        self.timeout_limit_seconds = 3
        self.social_media_list = [
            "facebook",
            "twitter",
            "linkedin",
            "instagram",
            "tiktok",
            "youtube"
        ]
        self.social_media_not_found = []

        self.data = read_list_companies("./wikicorpsv2.json")
        self.start_urls = list(map(lambda row: row['official_website'], self.data))

    def start_requests(self):
        for index, url in enumerate(self.start_urls):
            yield scrapy.Request(url,
                errback=self.parse_error,
                dont_filter=True,
                meta={
                'index':index,
                
                # 'download_timeout': self.timeout_limit_seconds
                })


    def getContactPageUrls(self, response):
        contact_keywords = [
            "contact",
            "call"
        ]
        urls = []
        for contact_keyword in contact_keywords:
            url = response.xpath(f"//a[contains(@href, '{contact_keyword}')]/@href").extract()
            urls.extend(url)
        
        unique_urls = []
        for url in urls:
            if url not in unique_urls:
                unique_urls.append(url)
        return unique_urls

    def getSocialMediaItem(self, response, social_media_list=None, item=None):
        if social_media_list is None:
            social_media_list = self.social_media_list
        if item is None:
            item = SocialMediaLinksItem()

        for social_media_name in social_media_list:
            social_url = response.xpath(f"//a[contains(@href, '{social_media_name}')]/@href").get()
            item[social_media_name] = social_url
            # print(social_media_name, " -> ", social_url)
            if social_url is None and social_url not in self.social_media_not_found:
                self.social_media_not_found.append(social_media_name)
        return item

    def parse_error(self, failure):
        item = self.data[failure.request.meta['index']]
        for social in self.social_media_list:
            item[social] = None
        # print(item)
        yield item

    def parse(self, response):
        print(f"Request #{response.meta['index']}", end='\r')
        # print(f"{response.request.url}")
        item = self.data[response.meta['index']]
        item = self.getSocialMediaItem(response, item=item)
        if len(self.social_media_not_found) > 0:
            contact_urls = self.getContactPageUrls(response)
            for url in contact_urls:
                resp = HtmlResponse(url)
                item = self.getSocialMediaItem(resp, self.social_media_not_found.copy(), item)
                self.social_media_not_found.clear()
        yield item