import scrapy
from ..items import CompanyWikiItem
import re

class CompanyWikiSpider(scrapy.Spider):
    def __init__(self):
        self.id_counter = 1

    name = "wikicorps"
    start_urls = [
        "http://en.wikipedia.org/wiki/List_of_mobile_network_operators_of_the_Middle_East_and_Africa",
        "http://en.wikipedia.org/wiki/List_of_mobile_network_operators_of_the_Americas",
        "http://en.wikipedia.org/wiki/List_of_mobile_network_operators_of_the_Asia_Pacific_region",
        "http://en.wikipedia.org/wiki/List_of_mobile_network_operators_of_Europe"
        ]
    
    def clean_operator(self, text):
        text = re.sub(r" \(.*\)", "", text) # remove (anything between parantheses)
        return text
    
    def process_wiki_url(self, text):
        # If index.php is found in url, it means 404 not found
        # if '/wiki' is not in url, usually it's the official website of business
        if "index.php" in text or "/wiki" not in text:
            return "https://null.com/"
        return "https://en.wikipedia.org" + text

    def parse(self, response):
        countries = response.xpath("//*[@class = 'mw-headline'][@id != 'See_also' and @id != 'References']//text()").extract()
        tables = response.css("h2 ~ .wikitable")
        items = []
        
        # For each country (and a table), create an item with (id, country, operator, url)
        for country, table_number in zip(countries, range(1,len(tables)+1)):
            operators = response.xpath(f"//table[@class='wikitable' and position()={table_number}]/tbody/tr[position()>1]/td[position()=2]/a/text()").extract()
            company_wiki_urls = response.xpath(f"//table[@class='wikitable' and position()={table_number}]/tbody/tr[position()>1]/td[position()=2]/a/@href").extract() 
            for operator, company_wiki_url in zip(operators, company_wiki_urls):
                item = CompanyWikiItem()

                item['id'] = self.id_counter
                item['country'] = country
                item['operator'] = self.clean_operator(operator)
                item['company_wiki_url'] = self.process_wiki_url(company_wiki_url)
                
                items.append(item)
                self.id_counter += 1
                yield item
        return None