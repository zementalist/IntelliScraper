import scrapy
from ..items import AiscraperItem
import re




class CompaniesSpider(scrapy.Spider):
    name = "Companies"

    start_urls = [
        "http://en.wikipedia.org/wiki/List_of_mobile_network_operators_of_the_Middle_East_and_Africa",
        "http://en.wikipedia.org/wiki/List_of_mobile_network_operators_of_the_Americas",
        "http://en.wikipedia.org/wiki/List_of_mobile_network_operators_of_the_Asia_Pacific_region",
        "http://en.wikipedia.org/wiki/List_of_mobile_network_operators_of_Europe"
        ]




    def parse(self, response):
        items = AiscraperItem()
        # countries = response.css("span.mw-headline::text").extract()
        # items['countries'] = countries
        # companies = response.css("table.wikitable").css("tbody").css("tr").extract()
        # items['companies'] = companies
        mix = response.css("div.mw-parser-output").extract()


        items['mix'] = mix

        yield items

