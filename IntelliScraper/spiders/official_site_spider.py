import scrapy
from ..items import SocialMediaLinksItem
from scrapy.http import HtmlResponse
from ..helper import *
import re

class OfficialSiteSpider(scrapy.Spider):
    name = 'official_site'

    def __init__(self):
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

    def parse(self, response):
        domain_regex = re.compile("^(?:https?:\/\/)?(?:[^@\n]+@)?(?:www\.)?([^:\/\n?]+)")

        current_url_domain = domain_regex.match(response.request.url).group().rstrip("/").replace("www.","")
        item_id = list(map(lambda sample: domain_regex.match(sample['official_website']).group().rstrip("/").replace("www.",""), self.data)).index(current_url_domain)
        item = self.data[item_id]

        item = self.getSocialMediaItem(response, item=item)
        if len(self.social_media_not_found) > 0:
            contact_urls = self.getContactPageUrls(response)
            for url in contact_urls:
                resp = HtmlResponse(url)
                item = self.getSocialMediaItem(resp, self.social_media_not_found.copy(), item)
                self.social_media_not_found.clear()
        yield item