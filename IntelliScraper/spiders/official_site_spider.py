import scrapy
from ..items import SocialMediaLinksItem
from scrapy.http import HtmlResponse


class OfficialSiteSpider(scrapy.Spider):
    name = 'official_site'
    start_urls = [
        "https://www.orange.com/en",
        "https://www.te.eg/wps/portal/te/Personal",
        "https://web.vodafone.com.eg/"

    ]
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
        item = self.getSocialMediaItem(response)
        if len(self.social_media_not_found) > 0:
            contact_urls = self.getContactPageUrls(response)
            for url in contact_urls:
                resp = HtmlResponse(url)
                item = self.getSocialMediaItem(resp, self.social_media_not_found.copy(), item)
                self.social_media_not_found.clear()
        yield item