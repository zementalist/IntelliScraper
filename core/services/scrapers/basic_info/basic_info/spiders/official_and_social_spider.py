
import scrapy
# from scrapy.crawler import CrawlerProcess
from ..items import GeneralItem
import re
import os
from datetime import datetime
class OperatorWikiSpider(scrapy.Spider):
    def __init__(self):
        self.id_counter = 1

    name = "all_operators_wiki_v2"
    items = []
    urls = 'https://en.wikipedia.org/wiki/Category:Lists_of_companies_by_country'
        
    # Get the path of the data folder for different machines
    storage_path = os.path.join(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))), 'data', 'scraped_data').replace('\\scrapers\\basic_info\\basic_info', '')
    save_path = r"\{}".format(os.path.join(storage_path, 'all_operators.json'))
  
    custom_settings = {
        "TWISTED_REACTOR": "twisted.internet.selectreactor.SelectReactor",
        'FEEDS': {
            save_path: {
                'format': 'json',
                "overwrite":True
            }
        }
    }

    # Method to extract products from company's Wiki page
    def getProducts(self, response):
        # Return list of products
        products = response.xpath('//table[@class="infobox vcard"]//th[contains(text(), "Products")]/following-sibling::td//li/text()').getall()
        return products

    # Method to extract edit date of the wiki page
    def getLastEditDate(self, response):
        # Extract the last edit date
        page_last_edit_date = response.css('li#footer-info-lastmod::text').get()
        if page_last_edit_date is not None:
            
            # Extract date and ignore the rest of 'This page was last edited on'
            #start_index = page_last_edit_date.index("on ") + 3
            #stop_index = page_last_edit_date.index(',')
            #page_last_edit_date_string = page_last_edit_date[start_index:stop_index]

            # Convert '2 March 2023' to 2023-03-02
            page_last_edit_date = datetime.strptime(page_last_edit_date.strip(), "This page was last edited on %d %B %Y, at %H:%M").strftime("%Y-%m-%d")
        
        return page_last_edit_date
    
    # Method to extract official website URL from Wiki (entity) page
    def getOfficialWebsite(self, response, company_name):
        
        # some page doesn't have info table, so the company website link is in external link section
        # it has text "company website"
        
        official_website = response.xpath('//a[contains(text(), "website")]/@href').get()


        # Extract the official website link from the Wikipedia page
        if official_website is None:
            official_website = response.css('table.infobox.vcard th:contains("Website") + td a::attr(href)').get()
        
        

        #if official_website is None:
        #    official_website = response.xpath('//a[contains(@href, "{}")]/@href'.format(company_name.split(' ')[0].lower())).extract
        
        # get all officaial links from this page
        if official_website is None:
            #official_website = response.xpath('//a[contains(@href, "hyundai")]/@href').extract()
            links = response.xpath('//a[contains(@class, "external text")]/@href').getall()
            pattern = re.compile(r"^https?://(?:www\.)[a-zA-Z0-9-_]+(\.[a-z]+)+$")
            formal_website_links = []
            for link in links:
                if pattern.match(link):
                    formal_website_links.append(link)
            official_website = formal_website_links        
        return official_website

    def prepare_string(self, string):
        # remove non alpha chars 
        new_string=''
        for i in string:
            if i.isalpha():
                new_string += i
            else:
                new_string += ' '
        return new_string.strip()
    
    def correctLink(self, link):
        if link and link.startswith('//'):
            return 'https:'+link
        return link
    
    def start_requests(self):
        yield scrapy.Request(url=self.urls, callback=self.parse_links)

    def parse_links(self, response):

        # lower_cat = soup.find_all('div', class_='mw-category mw-category-columns')[-1]

        companies_by_country = response.xpath('//div[@class="mw-category mw-category-columns"]')[1]
        
        all_links = companies_by_country.xpath('.//a/@href').extract()
        
        all_links = ['https://en.wikipedia.org' + link for link in all_links]

        for link in all_links:
            yield response.follow(url=link, callback=self.parseTableContent)

    def parseTableContent(self, response):
        
        try:
            table = response.xpath('//table[@class="wikitable sortable"]')[1]
        except:
            table = response.xpath('//table[@class="wikitable sortable"]')[0]
        rows = table.xpath('.//tr')[1:]

        # get country name from the link
        country = response.request.url.split('of_')[-1]
        for row in rows:
            cells = row.xpath('.//td')
        

            company_name = cells[0].xpath('.//a/text()').get()
            company_wiki_url = 'https://en.wikipedia.org' + cells[0].xpath('.//a/@href').extract_first()
            industry = cells[1].xpath('.//text()').get()
            sector = cells[2].xpath('.//text()').get()
            headquarter = cells[3].xpath('.//text()').get()
            founded = cells[4].xpath('.//text()').get()
            
            
            item = GeneralItem()
            item['id'] = self.id_counter
            item['country'] = self.prepare_string(country)
            item['headquarter'] = self.prepare_string(headquarter)
            item['operator_wiki_url'] = company_wiki_url
            item['company_name'] = self.prepare_string(company_name)
            item['founded'] = self.prepare_string(founded)
            item['industry'] = self.prepare_string(industry)
            item['sector'] = self.prepare_string(sector)
            
            item['numbers'] = None
            item['emails'] = None
            
            yield response.follow(url=company_wiki_url, callback=self.parseFromWikiPage, meta={'item':item})
            
            self.id_counter += 1

            #yield item
        return None
    
    def parseFromWikiPage(self, response):
        item = response.meta['item']
        item['product'] = self.getProducts(response)
        item['official_website'] = self.getOfficialWebsite(response, company_name=item['company_name'])
        item['page_last_edit_date'] = self.getLastEditDate(response)
        self.items.append(item)

        try:
            yield response.follow(url=item['official_website'], callback=self.parseSocialLinks, meta={'item':item})
        except:
            item['facebook']= None
            item['twitter']= None
            item['instagram']= None
            item['linkedin']= None
            item['youtube']= None
            item['tiktok'] = None
        
            yield item

    def parseSocialLinks(self, response):
        item = response.meta['item']
        # Extract links to the company's social media profiles
        facebook = self.correctLink(response.xpath('//a[contains(@href, "www.facebook.com")]/@href').extract_first())
        # TODO: make it work for both www.twitter.com and twitter.com
        twitter = self.correctLink(response.xpath('//a[contains(@href, "twitter.com")]/@href').extract_first())
        instagram = self.correctLink(response.xpath('//a[contains(@href, "www.instagram.com")]/@href').extract_first())
        youtube = self.correctLink(response.xpath('//a[contains(@href, "www.youtube.com")]/@href').extract_first())
        tiktok = self.correctLink(response.xpath('//a[contains(@href, "www.tiktok.com")]/@href').extract_first())
        linkedin = self.correctLink(response.xpath('//a[contains(@href, "www.linkedin.com")]/@href').extract_first())

        # Yield the results
        
        item['facebook']= facebook
        item['twitter']= twitter
        item['instagram']= instagram
        item['linkedin']= linkedin
        item['youtube']= youtube
        item['tiktok'] = tiktok

        yield item
        



