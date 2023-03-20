import scrapy
from ..items import CompanyWikiItem
import re

# Countries shift
# Companies with no links have no <a>, check and get td.innerText

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
    
    # def start_requests(self):
    #     for index, url in enumerate(self.start_urls):
    #         yield scrapy.Request(url, errback=self.parse_error)
        
    # def parse_error(self, failure):
    #     item = CompanyWikiItem()
    #     item['id'] = self.id_counter
    #     item['country'] = country
    #     item['operator'] = self.clean_operator(operator)
    #     item['company_wiki_url'] = self.process_wiki_url(company_wiki_url)
        
    #     yield item

    def clean_operator(self, text):
        text = re.sub(r" \(.*\)", "", text) # remove (anything between parantheses)
        return text
    
    def process_wiki_url(self, text):
        # If index.php is found in url, it means 404 not found
        # if '/wiki' is not in url, usually it's the official website of business
        if "index.php" in text or "/wiki" not in text:
            return f"https://null.com"
        return "https://en.wikipedia.org" + text

    def parse(self, response):
        countries = response.xpath("//*[@class = 'mw-headline'][@id != 'See_also' and @id != 'References' and @id != 'Footnotes' and @id != 'External_links']//text()").extract()
        tables = response.css("h2 ~ .wikitable")
        items = []
        # print(countries)
        # For each country (and a table), create an item with (id, country, operator, url)
        for country, table_number in zip(countries, range(1,len(tables)+1)):

            operators = response.xpath(f"//table[contains(@class,'wikitable')][position()={table_number}]/tbody/tr[position()>1]/td[position()=2]/a/text()").extract()
            operators_without_url = response.xpath(f"//table[contains(@class,'wikitable')][position()={table_number}]/tbody/tr[position()>1]/td[position()=2][not(a)]/text()").extract()
            
            corrupted_operators_without_url = response.xpath(f"//table[contains(@class,'wikitable')][position()={table_number}]/tbody/tr[position()>1]/td[position()=2][not(br)]/text()").extract()
            operators_without_url = list(set(operators_without_url) - set(corrupted_operators_without_url) - set([' ', '\n', '']))
            
            company_wiki_urls = response.xpath(f"//table[contains(@class,'wikitable')][position()={table_number}]/tbody/tr[position()>1]/td[position()=2]/a/@href").extract()
            company_without_wiki_url = [""] * len(operators_without_url)

            operators.extend(operators_without_url)
            company_wiki_urls.extend(company_without_wiki_url)

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