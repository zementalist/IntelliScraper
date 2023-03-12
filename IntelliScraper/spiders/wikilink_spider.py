import scrapy
import unicodedata
import re
from datetime import datetime
from IntelliScraper import csv_reader
from ..items import WikilinkItem


class WikilinkSpider(scrapy.Spider):
    name = "wikilink"

    def __init__(self):
        super(WikilinkSpider)
        self.info_card_tr_pattern = "//table[@class='infobox vcard']/tbody/tr"
        self.start_urls = csv_reader.pluck(csv_reader.read("wikicorps.csv"),"url")

    def getCompanyName(self, response):
        name = response.css("#firstHeading span::text").get()

        # Company name is also available through URL, extract it
        # and return whatever is NOT None
        name_from_url = response.url[response.url.rfind("/")+1:]
        return name_from_url if name is None else name

    def getIndustry(self, response):

        # Function to remove any special characters and extra spaces
        def remove_non_alpha(text):
            # remove non alpha
            text = re.sub("[^a-zA-Z ]", "", text)
            # remove spaces at beginning | at end | multi-consecutive spaces
            text = re.sub("^\s+|\s+$|\s\s+", "", text)
            text = text.capitalize()
            return text

        # Extract list of industries
        list_of_industries = response\
        .xpath(f"{self.info_card_tr_pattern}/th[text()='Industry']/following-sibling::td//text()")\
        .extract()

        # Clean industry keywords
        list_of_industries = list(map(remove_non_alpha, list_of_industries))
        return list_of_industries

    def getProducts(self, response):
        # Return list of products
        return response\
        .xpath(f"{self.info_card_tr_pattern}/th/a[text()='Products']/../following-sibling::td/div/ul/li//text()")\
        .extract()
    
    def getFounded(self, response):
        founded_as_list = response\
            .xpath(f"{self.info_card_tr_pattern}/th[text()='Founded']/following-sibling::td")\
            .css("::text")\
            .extract()
        
        # Remove non utf-8 characters
        founded_as_str = unicodedata.normalize("NFKD", " ".join(founded_as_list))

        # Extract any 4 consecutive digits (recommended to use r'1\d{3}|2\d{3}')
        founded_as_list_of_years = list(map(int, re.findall(r"\d{4}", founded_as_str)))

        # Minimum year is the year of foundation
        founded = min(founded_as_list_of_years)
        return founded

    # Method to extract edit date of the wiki page
    def getLastEditDate(self, response):
        page_last_edit_date = response.css("#footer-info-lastmod::text").get()
        if page_last_edit_date is not None:
            
            # Extract date and ignore the rest of 'This page was last edited on'
            start_index = page_last_edit_date.index("on ") + 3
            stop_index = page_last_edit_date.index(',')
            page_last_edit_date_string = page_last_edit_date[start_index:stop_index]

            # Convert '2 March 2023' to 2023-03-02
            page_last_edit_date = datetime.strptime(page_last_edit_date_string, "%d %B %Y").strftime("%Y-%m-%d")
        
        return page_last_edit_date

    def parse(self, response):
        company_name = self.getCompanyName(response)
        industries = self.getIndustry(response)
        products = self.getProducts(response)
        founded = self.getFounded(response)
        page_last_edit_date = self.getLastEditDate(response)
        
        item = WikilinkItem()
        item['company_name'] = company_name
        item['founded'] = founded
        item['industry'] = industries
        item['product'] = products
        item['page_last_edit_date'] = page_last_edit_date
        
        yield item