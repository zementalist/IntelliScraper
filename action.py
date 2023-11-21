import os
import re
import json
import torch
import requests
import numpy as np

# from spacy import  # Takes too long

from datetime import date, datetime
from parsel import Selector
from bs4 import BeautifulSoup
from ytspider import YTSChannel, YTSVideo
from core.services.classifiers.campaign_classifier_inference import CampaignClassifier
from core.services.classifiers.sentiment_classifier_inference import SentimentClassifier
from core.services.scrapers.social.twitter_scraper_selenium import TwitterScraper

c_classifier = None
s_classifier = None


def CheckIfCampaign(input):
    global c_classifier
    if c_classifier is None:
        model = torch.load(r".\core\services\classifiers\weights\campaign-bert-mini.pt",map_location=torch.device('cpu'))
        c_classifier = CampaignClassifier(model)
    return c_classifier.predict_if_campaign(input)
    
def AnalyzeSentiment(input):
    global s_classifier
    if s_classifier is None:
        # f = open("sentiment-analysis-model-bert-mini.pt", 'rb')
        # model = pickle.load(f)
        # model = SentBertCls().load_state_dict(model)
        # model.to("cpu")
        # model.eval()
        model = torch.load(r".\core\services\classifiers\weights\sentiment-bert-mini.pt",map_location=torch.device('cpu'))
        s_classifier = SentimentClassifier(model)
        # model_path = 'sentiment-analysis-model-bert-mini.pt'
        # self.model = BertClassifier()
        # self.model.load_state_dict(model)
        # self.model.eval()
        # f = open(model_path, 'rb')
        # model = pickle.load(f)
        # torch.save(model.state_dict(), "model.pt")
        # print(model)
    return s_classifier.analyze_sentiment(input)




class Action:
    def __init__(self, n_items, publish_date_end):
        self.n_items = n_items
        self.publish_date_end = publish_date_end
        self.__storage_path = os.path.join(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))), 'data', 'scraped_data').replace('\\scrapers', '')
        
    def execute(self, url):
        # Returns array( object(offerText, popularityRate, subjectivityRate, satisfactionRate, interactions) )
        return []



class YouTubeAction(Action):
    def __init__(self, n_items, publish_date_end):
        super(YouTubeAction, self).__init__(n_items, publish_date_end)

    # def getPopularityRate(self, offer):
    #     if "views" in offer:
    #         views = offer["views"]
    #     if "likes" in offer:
    #         likes = offer["likes"]

    def execute(self, url):
        offers = []
        channelName = url
        print(url)
        channel = YTSChannel()
        channel.scrape(channelName).withVideos(self.n_items)
        channelData = channel.get()
        channelName = list(channelData.keys())[0]
        print(channelData)
        print(channelName)
        if channelName in channelData:
            video_ids = [single_video["id"] for single_video in channelData[channelName]["videos"]]
            print(video_ids)
            videos = YTSVideo()
            videos = videos.scrape(video_ids).withComments(10)
            videosWithComments = videos.get()
            # print(videosWithComments)
            scraped_videos = [video for video in list(videosWithComments.values())]
            [video.update(channelVideo) for video, channelVideo in zip(scraped_videos, channelData[channelName]['videos'])]
            
            total_views = 0
            for video in scraped_videos:
                # videos = YTSVideo()
                # videos = videos.scrape(id).withComments(10)
                # video = videos.get()[id]
                # print(f"Video {id}")
                # video = videosWithComments[id]
                # print(video)
                
                description = video["shortDescription"]
                is_campaign = CheckIfCampaign(description)[0]
                if is_campaign:
                    offer = {}
                    offer["content"] = description.replace("\n", " ")
                    offer["views_str"] = video["views_count"]
                    offer["views_int"] = video["viewCount"]
                    offer["video"] = f"https://www.youtube.com/watch?v={video['videoId']}"
                    offer["img"] = video["thumbnail"]["thumbnails"][-1]["url"]
                    offer["publish date"] = video['publish_at']
                    offer["satisfaction rate"] = ""

                    total_views += int(offer["views_int"])
                    if "comments" in video:
                        comments = video["comments"]
                        sentiments = AnalyzeSentiment(comments)
                        print("This is sentiment")
                        print(sentiments)
                        satisfaction_rate = round((np.count_nonzero(sentiments) / len(sentiments)) * 100,2)
                        offer["satisfaction rate"] = str(satisfaction_rate) + "%"
                    
                    # if offer content has URL, scrape it for offer details
                    offer_urls = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', offer["content"])
                    official_website_offer_crawler = OfficialWebsiteOfferAction()
                    for url in offer_urls:
                        # Crawl offer page
                        official_offer_details = official_website_offer_crawler.execute(url)
                        print("Officla Offer:")
                        print(official_offer_details)
                        # What to do with it ?

                    # print(satisfaction_rate)
                    offers.append(offer)
        for offer in offers:
            offer["popularity rate"] = str(round((int(offer["views_int"]) / total_views) * 100, 2)) + "%"
            offer["views"] = offer["views_str"]
            del offer["views_str"]
            del offer["views_int"]
        print(offers)
        # offers = [
        #     {
        #         "offer": "",
        #         #popularity:20%,
        #         "interactions":50,
        #         "subjectivity": 30,
        #         "satisfaction_rate": 20
        #     }
        # ]
        return offers

class TwitterAction(Action):
    def __init__(self, n_items, publish_date_end):
        super(TwitterAction, self).__init__(n_items, publish_date_end)
    def execute(self, url):
        # Get the username form the URL
        match = re.search(r'twitter.com/(\w+)', url)
        if match:
            username = match.group(1)

        twitter_scraper = TwitterScraper(username)
        tweets = twitter_scraper.get_tweets_information(self.n_items)
        
        offers = []
        total_views = 0
        
        for tweet in tweets:
            is_campaign = CheckIfCampaign(tweet['text'])[0]
            if is_campaign:
                offer = {}
                offer["content"] = tweet['text']
                offer["views"] = tweet["view_count"]
                # TODO: replace id with the status link like this https://twitter.com/telecomegypt/status/1649503624618299392
                offer["id"] = tweet["id"]
                offer["like_count"] = tweet['like_count']
                offer["satisfaction rate"] = ""
                views = offer["views"].replace(',', '')
                if views == '':
                    views = 0
                total_views += int(views)
                if tweet["replies"]:
                    sentiments = AnalyzeSentiment(tweet["replies"])
                    satisfaction_rate = round((np.count_nonzero(sentiments) / len(sentiments)) * 100,2)
                    offer["satisfaction rate"] = str(satisfaction_rate) + "%"
                offers.append(offer)
                
        for offer in offers:
            views = offer["views"].replace(',', '')
            if views == '':
                views = 0
            offer["popularity rate"] = str(round((int(views) / total_views) * 100, 2)) + "%"

        return offers


class OfficialWebsiteOfferAction(Action):
    def __init__(self):
        super(OfficialWebsiteOfferAction, self)
        # self.nlp = load("en_core_web_sm")
        en_core_web_sm = __import__("en_core_web_sm")
        self.nlp = en_core_web_sm.load()
        self.keywords = "discount|offer|deal|special|package|benefit|prepaid|price|promo|promotion|subscribe|price|pay|plan"
    
    def execute(self, url):
        result = []
        try:
            response = requests.get(url)
        except:
            return result
        if response.status_code == 200:
            offers_tabular = self.extract_tabular_offers(response)
            offers_tabular = json.loads(json.dumps(offers_tabular).replace("\xa0", ''))

            # If any tabular offers, return in (there's no need to scrape text inside)
            if len(offers_tabular) > 0:
                result = offers_tabular
            else:
                # If no tabular offers, find textual using Xpath and Soup techniques
                offers_xpath = self.extract_offers_by_xpath(response)
                offers_bsoup = self.extract_offers_by_soup(response)

                # Merge offers from the two techniques
                offers = offers_xpath + offers_bsoup

                # [offer for offer in offers if offers.index(offer) == len(offers) - 1 - offers[::-1].index(offer)]
                result = offers
        return offers

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
            return [result]
                            
            
        offers = []
        response = Selector(response.text)
        tables = response.css("table").extract()
        for table in tables:
            tableText = BeautifulSoup(table)
            if re.search(self.keywords, tableText.get_text(), re.IGNORECASE):
                table_data = formatTable(tableText)
                offers.append(table_data)
        return offers
        

    def extract_offers_by_xpath(self, response):
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
        response = Selector(response.text)
        offers = []
        for element in textual_html_elements:
            for word in keywords:
                list_of_texts = response.xpath(f"//{element}/text()[contains({lowercase_xpath_func},'{word}')]").extract()
                clean_offers = list(map(lambda text: re.sub(r"\W+", " ",text).strip(), list_of_texts))
                unique_offers = [offer for offer in clean_offers if offer not in offers]
                offers.extend(unique_offers)
        offers = [offer for offer in offers if offers.index(offer) == len(offers) - 1 - offers[::-1].index(offer)]
        # end = datetime.now()
        # duration = end - start
        # print("Time Complexity: " + str(duration.total_seconds()))
        # print("\n\n".join(offers))
        # print("\n\n\n\n\n")
        return offers

    def extract_offers_by_soup(self, response):
        
        # start = datetime.now()
        keywords = self.keywords
        offers = []
        elements = []
        entities = []
        counter = 3
        soup = BeautifulSoup(response.text)
        target_html_tags = ["div"]#["span", "li","p", "h1", 'h2', 'h3', 'h4', 'h5', 'h6']
        for element in soup.find_all(target_html_tags):
            # if element.name not in things:
            #     things[element.name] = []
            
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
        # end = datetime.now()
        # duration = end - start
        # print("Time Complexity: " + str(duration.total_seconds()))
        # print("\n\n".join(offers))
        return offers

class ActionFactory:
    
    def make(self, social_platform_name, n_items, publish_date_end):
        # if type(social_platform_name) != str or type(n_items) != int or type(publish_date_end) != str:
        #     raise ValueError("Invalid data type, required social_platform_name: str, n_items: int, publish_date_end: str")
        social_platform_name = social_platform_name.lower()
        if social_platform_name == "twitter":
            return TwitterAction(n_items, publish_date_end)
        elif social_platform_name == "youtube":
            return YouTubeAction(n_items, publish_date_end)
        else:
            raise ValueError(f"Social platform ({social_platform_name}) is unavailable right now.")

# if __name__ == "__main__":
#     # YouTubeAction(1, None).execute("@VodafoneEgypt")
#     AnalyzeSentiment("حلو جدا الاعلان ده عجبني و ادهشني")
# else:
#     print("NO")

# def test():
#     print(AnalyzeSentiment("حلو جدا الاعلان ده عجبني و ادهشني"))
#     print("GOOD")
# YouTubeAction(5, None).execute("@VodafoneEgypt")
