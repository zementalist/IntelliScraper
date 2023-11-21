import scrapy
from bs4 import BeautifulSoup
import spacy
import re
import json
from datetime import datetime
# Find all pages with promotion keywords
# Run element by element with spacy
# Check if element contains something about offer
    # Check if element is table
        # handle table (extrct each column as single offer)
    # Check if element has direct children (p, a, span, h1-h6)
        # Extract whole element text as offer single

class NameSiteSpider(scrapy.Spider):
    def __init__(self):
        super(NameSiteSpider,self)
        self.nlp = spacy.load("en_core_web_sm")
        self.keywords = "discount|offer|deal|special|package|benefit|prepaid|price|promo|promotion|subscribe|price|pay|plan"
    name = "offers"
    start_urls = [
        # "https://te.eg/wps/portal/te/Personal/Promotions/Mobile-Promotions?1dmy&urile=wcm%3apath%3a%2Fte%2Fresidential%2Fpromotions-revamp%2Fmobile%2Fprepaid%2Framadan%2Brecharge%2Bpromo%2B2023%2Framadan%2Brecharge%2Bpromo",
        # "https://web.vodafone.com.eg/en/flex-coins-program",
        "https://www.chooseyourmobile.com/stc-ksa-internet-packages/",
        # "https://te.eg/sl/SuperKix",
        # "https://te.eg/wps/portal/te/Personal/Promotions/Internet-Promotions/!ut/p/z1/jY_BCsIwEAU_KS9bTc2xGFqW2JZa1JqL5FQCWj2I32-UgodidW8LM-yscKITbvCP0Pt7uA7-HPejU6clDDFabIo9KzS2ktzmCwKTOLwB2xiSdQFba6WRlWygtylhRcL9488ALx9fJkP03ewJq0bgk2irJCZqg3WuJMp0Akx_-FVxu-w6BO6f7hkT5A!!/dz/d5/L0lDUmlTUSEhL3dHa0FKRnNBLzROV3FpQSEhL2Fy/?1dmy&urile=wcm%3apath%3a%2Fte%2Fresidential%2Fpromotions-revamp%2Fdata%2Ftop-up-recharge%2Fx2%2Byour%2Bfixed%2Binternet%2Btop-up%2Bpromo",
        # "https://te.eg/wps/portal/te/Personal/Mobile/Prepaid-Agda3-Sha7na/!ut/p/z1/jZDbCoJQEEW_pQ-I2Z285KP3TEvMNDsvYSUmWQZJ359WECRd5m1gbWbNJk4J8VN6LfK0LqpTWjb7iktrEQZzEMKzNUdCEHuRZsXCEAAt74AbGGzg23B9RVKgTh0DylxmGDHi_-S_AG0eH0Zt8_ztRGibUC1T9Bbygulj9gReiu5s2CgqBnRLGmAqd4DuD78sJsTzsto8CjsI--iqEr_UaZ1Rsi2rS7ajMeh8jBIUTp9vhN4NH6F1xw!!/dz/d5/L0lDUmlTUSEhL3dHa0FKRnNBLzROV3FpQSEhL2Fy/"
        # "https://stcpay.com.sa/offers/"
        # "https://te.eg/wps/portal/te/Personal/Promotions/Mobile-Promotions?1dmy&urile=wcm%3apath%3a%2Fte%2Fresidential%2Fpromotions-revamp%2Fmobile%2Fprepaid%2F015_offer%2F015_offer"
    ]
    # def start_requests(self):
    #     urls = ['https://en.wikipedia.org/wiki/Vodafone']
    #     for url in urls:
    #         yield scrapy.Request(url=url, callback=self.parse)

    def extract_tabular_offers(self, response):

        def formatTable(tableText):
            table_data = [[cell.text for cell in row("td")]
                                    for row in tableText("tr")]
            
            min_length = min([len(item) for item in table_data])
            max_length = max([len(item) for item in table_data])

            result = dict()
            if min_length == max_length:
                for i, item in enumerate(table_data):
                    if i == 0:
                        for col in item:
                            result[col] = []
                    else:
                        for i,col in enumerate(result.keys()):
                            result[col].append(item[i])
            else:
                result = table_data
            return result
                            
            
        offers = []
        tables = response.css("table").extract()
        for table in tables:
            tableText = BeautifulSoup(table)
            if re.search(self.keywords, tableText.get_text(), re.IGNORECASE):
                table_data = formatTable(tableText)
                offers.append(table_data)
        return offers
        

    def extract_offers_by_xpath(self, response):
        start = datetime.now()
        offers = []
        entities = []
        keywords = self.keywords
        keywords_to_except = ["chrome", "safari", 'edge', 'firefox']

        doc = self.nlp(BeautifulSoup(response.text).get_text())
        for ent in doc.ents:
            if ent.label_ in ['PRODUCT', 'MONEY', 'PERCENT'] or re.search(r"\d+X|"+keywords,ent.text, re.IGNORECASE):
                entities.append(ent.text.lower())
                # print(ent)
        keywords = keywords.split("|")
        keywords.extend(entities)

        keywords = list(set(keywords) - set(keywords_to_except))
        # print(keywords)

        # I Removed [li, a, span]
        textual_html_elements = ["p", "span", "li", "h1", "h2", "h3", "h4", "h5", "h6"]
        lowercase_xpath_func = "translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')"

        offers = []
        for element in textual_html_elements:
            for word in keywords:
                list_of_texts = response.xpath(f"//{element}/text()[contains({lowercase_xpath_func},'{word}')]").extract()
                clean_offers = list(map(lambda text: re.sub(r"\W+", " ",text).strip(), list_of_texts))
                unique_offers = [offer for offer in clean_offers if offer not in offers]
                offers.extend(unique_offers)
        offers = [offer for offer in offers if offers.index(offer) == len(offers) - 1 - offers[::-1].index(offer)]
        end = datetime.now()
        duration = end - start
        # print("Time Complexity: " + str(duration.total_seconds()))
        # print("\n\n".join(offers))
        # print("\n\n\n\n\n")
        return offers

    def extract_offers_by_soup(self, response):
        
        start = datetime.now()
        keywords = self.keywords
        offers = []
        elements = []
        entities = []
        counter = 3
        soup = BeautifulSoup(response.text)
        things = {}
        target_html_tags = ["div"]#["span", "li","p", "h1", 'h2', 'h3', 'h4', 'h5', 'h6']
        for element in soup.find_all(target_html_tags):
            if element.name not in things:
                things[element.name] = []
            
            doc = self.nlp(element.get_text())
            for ent in doc.ents:
                is_offer = (ent.label_ in ['PRODUCT', 'MONEY', 'PERCENT']) or (ent.text.lower() in keywords.split("|") or (re.search(r"\d+X|"+keywords,ent.text, re.IGNORECASE)))
                if is_offer:
                    entities.append(re.sub('[^a-zA-Z0-9 .]','',ent.text))
            for sent in doc.sents:
                pat = keywords.split("|")
                pat.extend(entities)
                pat = "|".join(pat)
                if re.search(pat, sent.text, re.IGNORECASE):
                    for ent in entities:
                        if ent in sent.text:
                            clean_text = re.sub(r"[^\w. ]", " ", sent.text).strip()
                            clean_text = re.sub(" {2,}", " ", clean_text).strip()
                            if clean_text not in offers:
                                offers.append(clean_text)
            # things[tag] = offers
        end = datetime.now()
        duration = end - start
        # print("Time Complexity: " + str(duration.total_seconds()))
        # print("\n\n".join(offers))
        return offers

    def parse(self, response):
        # Find tabular offers in a page
        offers_tabular = self.extract_tabular_offers(response)
        offers_tabular = json.loads(json.dumps(offers_tabular).replace("\xa0", ''))

        # If any tabular offers, return in (there's no need to scrape text inside)
        if len(offers_tabular) > 0:
            print(offers_tabular)
            return None#offers_tabular

        # If no tabular offers, find textual using Xpath and Soup techniques
        offers_xpath = self.extract_offers_by_xpath(response)
        offers_bsoup = self.extract_offers_by_soup(response)

        # Merge offers from the two techniques
        offers = offers_xpath + offers_bsoup

        # [offer for offer in offers if offers.index(offer) == len(offers) - 1 - offers[::-1].index(offer)]
        print(offers)
        return None#offer-