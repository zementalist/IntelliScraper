from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from datetime import datetime
from pprint import pprint
import time
import os
import re

class TwitterScraper():

    def __init__(self, user) -> None:
        
        self.user = user
        # Universal storage path
        self.__storage_path = os.path.join(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))), 'data', 'scraped_data').replace('\\scrapers', '')
        # Specify the path to chromedriver.exe
        self.__webdriver_path = os.path.join(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))), 'chromedriver.exe')
        # Drivers options
        self.chrome_options = webdriver.ChromeOptions()
        # To get rid of notifications
        self.prefs = {"profile.default_content_setting_values.notifications" : 2}
        self.chrome_options.add_experimental_option("prefs",self.prefs)
        
        self.driver = webdriver.Chrome(self.__webdriver_path, options=self.chrome_options)
  
    def login(self):
        '''Log in twitter to have full access'''
        #open the webpage
        self.driver.get("https://twitter.com/i/flow/login")

        time.sleep(10)

        # enter username
        # TODO: make username and password as parameters taken from configuration file
        username = self.driver.find_element(By.TAG_NAME, "input")
        username.send_keys("Mohamed4853448")

        # press on the "next" button
        all_buttons = self.driver.find_elements(By.XPATH, "//div[@role='button']")
        all_buttons[-2].click()

        time.sleep(5)

        # enter password
        password = self.driver.find_element(By.XPATH, "//input[@type='password']")
        password.send_keys("iammohamed12345")

        time.sleep(5)

        # press on the login button
        all_buttons = self.driver.find_elements(By.XPATH, "//div[@role='button']")
        all_buttons[-1].click()

        time.sleep(10)
        
    def get_tweets_by_count(self, n_items):
        '''Get list of tweets links'''
        # Login to twitter
        self.login()
        
        self.driver.get(f"https://www.twitter.com/{self.user}/")
        time.sleep(5)
        
        all_anchors = set()
        
        # each scroll returns roughly 4 links
        n_scrolls = n_items // 4
        
        # Number of times PAGE DOWN key pressed
        number_of_PD = 6
        
        #scroll down and gets links
        for j in range(0, n_scrolls):
            print("scroll ======> ", j)
            anchors = []
            #target all the link elements on the page
            anchors = self.driver.find_elements(by=By.TAG_NAME, value='a')
            anchors = [a.get_attribute('href') for a in anchors]
            #narrow down all links to tweets links only
            anchors = [a for a in anchors if str(a).startswith(f"https://twitter.com/{self.user}/status/")]
            anchors = [a for a in anchors if str(a[-8]).isdigit()]
            
            for a in anchors:
                if (str(a).startswith(f"https://twitter.com/{self.user}/status/") and str(a[-8]).isdigit()):
                    all_anchors.add(a)
            
            # Use this for logging        
            # print('Found ' + str(len(anchors)) + ' links to posts')

            # press PAGE DOWN key
            for i in range(number_of_PD):
                self.driver.find_element(by=By.TAG_NAME, value='body').send_keys(Keys.PAGE_DOWN)
                time.sleep(0.1)
            
            time.sleep(5)
            
        # Returns a list of distinct links
        pprint(all_anchors)
        return all_anchors
            
    def get_tweets_information(self, n_items):
        '''Scrapes tweets for specific information'''
        # Get tweets_links
        tweets_links = self.get_tweets_by_count(n_items)
        tweets_list = []
        tweet_dict = {}
        
        for tweet in tweets_links:
            self.driver.get(tweet)
            time.sleep(3)
            
            # Get tweet id
            tweet_dict['id'] = re.findall(r"/(\d+)", tweet)[-1]
            
            # Get tweet content
            tweet_dict['text'] = self.__get_element('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/section/div/div/div[1]/div/div/article/div/div/div[3]/div[2]')
            
            # Get tweet view count    
            tweet_dict['view_count'] = self.__get_element('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/section/div/div/div[1]/div/div/article/div/div/div[3]/div[5]/div/div[1]/div/div[3]/span/div/span/span/span')
            
            # Get tweet like count    
            tweet_dict['like_count'] = self.__get_element('/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/section/div/div/div[1]/div/div/article/div/div/div[3]/div[6]/div[2]/a/div/span/span/span')
            
            # Get tweet datetime    
            raw_datetime = self.__get_element('/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/section/div/div/div[1]/div/div/article/div/div/div[3]/div[5]/div/div[1]/div/div[1]/a/time')
            if raw_datetime != '':
                date_object = datetime.strptime(raw_datetime, "%I:%M %p · %b %d, %Y")
                tweet_dict['date_time'] = date_object.strftime("%Y-%m-%d")
            else:
                tweet_dict['date_time'] = 'null'
            
            # Get tweet replies
            replies = set()
            users = set()
            replies_length = 0
            ## Gets replies and users with scrolls and halts at the end of the page
            while True:
                self.driver.find_element(by=By.TAG_NAME, value='body').send_keys(Keys.PAGE_DOWN)
                self.driver.find_element(by=By.TAG_NAME, value='body').send_keys(Keys.PAGE_DOWN)
    
                for i in range(1, 50):
                    # For users
                    user_elements = self.driver.find_elements(by=By.XPATH, value=f'/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/section/div/div/div[{i}]/div/div/article/div/div/div[2]/div[2]/div[1]/div/div[1]/div/div/div[1]/div/a')
                    for element in user_elements:
                        users.add(element.get_attribute('href'))
                    
                    # For replies
                    elements = self.driver.find_elements(by=By.XPATH, value=f'/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/section/div/div/div[{i}]/div/div/article/div/div/div[2]/div[2]/div[2]/div')
                    for element in elements:
                        replies.add(element.text)
                        
                if len(replies) == replies_length:
                    break
                else:
                    replies_length = len(replies)
            
            tweet_dict['replies'] = list(replies)
            tweet_dict['users_replied'] = list(users)
            
            tweets_list.append(tweet_dict)
            tweet_dict = {}
            
        return tweets_list
        
    def __get_element(self, x_path):
        '''get specified element using XPATH string'''
        
        elements = self.driver.find_elements(by=By.XPATH, value=x_path)
        result = ''
        for element in elements:
            result = element.text
            
        return result

        
        
# # testing the class      
# def main():
    
#     ts = TwitterScraper('telecomegypt')
#     pprint(ts.get_tweets_information(5))
    
# if __name__ == "__main__":
#     main()