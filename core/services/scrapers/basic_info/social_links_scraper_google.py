from bs4 import BeautifulSoup
import requests
from googlesearch import search   
import re

class SocialLinks():
    def __init__(self, page_url):
        self.page_url = page_url
        self.company_name = ''


    def filter_social_links(self, links):
        social_links = {}
        for link in links:
            if 'facebook' in link:
                social_links['facebook'] = link
            elif 'linked' in link:
                social_links['linkedin'] = link
            elif 'insta' in link:
                social_links['instagram'] = link
            elif 'twitter' in link:
                social_links['twitter'] = link
            elif 'youtube' in link:
                social_links['youtube'] = link
        return social_links


    def get_name_from_page_link(self, link):
        m = re.search('www\.(.+?)\.', link)

        if m:
            found = m.group(1)

        return found

    def get_links_from_search(self, query):
        mylinks = []
        for j in search(query, num_results=10):
            mylinks.append(j) 

        return mylinks

    def get_social_links(self):

        res = requests.get(self.page_url)

        soup = BeautifulSoup(res.text)

        all_links = [link['href'] for link in soup.find('footer').find_all(href=True)]

        social_links = self.filter_social_links(all_links)

        if len(social_links) == 0:
            self.company_name = self.get_name_from_page_link(self.page_url)
            search_links = self.get_links_from_search(self.company_name)

            social_links = self.filter_social_links(search_links)
        
        return social_links


        