import scrapy
import sys

sys.path.append(r'C:\Users\maryam.khalifa\Desktop\name_site')
class NameSiteSpider(scrapy.Spider):
    name = "name_site"

    def start_requests(self):
        urls = ['https://en.wikipedia.org/wiki/Vodafone']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        data = response.xpath('.//table[@class = "infobox vcard"]')
        yield {
               'name': data.xpath('.//caption[@class="infobox-title fn org"]//text()')[0].get(),
               'web_site': data.xpath('//span[@class="url"]/a/@href')[0].get()
           }
        
