import scrapy
import unicodedata
import re
from datetime import datetime

class WikilinkSpider(scrapy.Spider):
    name = "wikilink"
    start_urls = [
            "https://en.wikipedia.org/wiki/Netflix"
    ]
    def __init__(self):
        super(WikilinkSpider)
        self.info_card_tr_pattern = "//table[@class='infobox vcard']/tbody/tr"

    def getCompanyName(self, response):
        name = response.css("#firstHeading span::text").get()
        name_from_url = response.url[response.url.rfind("/")+1:]
        return name_from_url if name is None else name

    def getIndustry(self, response):

        def remove_non_alpha(text):
            # remove non alpha
            text = re.sub("[^a-zA-Z ]", "", text)
            # remove spaces at beginning | at end | multi-consecutive spaces
            text = re.sub("^\s+|\s+$|\s\s+", "", text)
            text = text.capitalize()
            return text

        list_of_industries = response\
        .xpath(f"{self.info_card_tr_pattern}/th[text()='Industry']/following-sibling::td//text()")\
        .extract()
        list_of_industries = list(map(remove_non_alpha, list_of_industries))
        # list_of_industries = str_of_industres.split()
        return list_of_industries

    def getProducts(self, response):
        return response\
        .xpath(f"{self.info_card_tr_pattern}/th/a[text()='Products']/../following-sibling::td/div/ul/li//text()")\
        .extract()
    
    def getFounded(self, response):
        founded_as_list = response\
            .xpath(f"{self.info_card_tr_pattern}/th[text()='Founded']/following-sibling::td")\
            .css("::text")\
            .extract()
        founded_as_str = unicodedata.normalize("NFKD", " ".join(founded_as_list))
        founded_as_list_of_years = list(map(int, re.findall(r"\d{4}", founded_as_str)))
        founded = min(founded_as_list_of_years)
        return founded

    def getLastEditDate(self, response):
        page_last_edit_date = response.css("#footer-info-lastmod::text").get()
        if page_last_edit_date is not None:
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
        
        row = {
            "company_name":company_name,
            "founded":founded,
            "industry":industries,
            "products":products,
            "page_last_edit_date":page_last_edit_date
        }
        print(row)
        yield row