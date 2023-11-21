#Importing libraries 

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import time 
import os

class MapsScraper():
    
    def __init__(self):
        # Universal storage path
        self.__storage_path = os.path.join(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))), 'data', 'scraped_data').replace('\\scrapers', '')
        # Specify the path to chromedriver.exe
        self.__webdriver_path = os.path.join(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))), 'chromedriver.exe')
        # Drivers options
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(self.__webdriver_path, options=self.chrome_options)
        #Loading Selenium Webdriver 
        wait = WebDriverWait(self.driver, 5)

    def get_address(self, location = 'Egypt', query = "Telecom Egypt", n_results=None):
        
        '''
        parameters: location, name of the place, num_results
        return : list of first 6 search results from google maps [[name, longitude, lattitude, adress]]
        '''
        #Opening Google maps 
        self.driver.get("https://www.google.com/maps")
        time.sleep(3)
        
        searc_hbox=self.driver.find_element('xpath', '/html/body/div[3]/div[9]/div[3]/div[1]/div[1]/div[1]/div[2]/form/div[2]/div[3]/div/input[1]')
        searchbox.send_keys(location)
        searchbox.send_keys(Keys.ENTER)
        time.sleep(2)
        cancelbut=self.driver.find_element(By.CLASS_NAME, 'gsst_a')
        cancelbut.click()
        searchbox.send_keys(query)
        searchbox.send_keys(Keys.ENTER)
        time.sleep(3)
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        SCROLL_PAUSE_TIME = 5
        number = 1

        time.sleep(2)
        while True:
            number = number+1

            # Scroll down to bottom
            xpath = '/html/body/div[3]/div[9]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]'
            ele = self.driver.find_element('xpath', xpath)
            self.driver.execute_script('arguments[0].scrollBy(0, 5000);', ele)

            # Wait to load page

            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            print(f'last height: {last_height}')

            ele = self.driver.find_element('xpath', xpath)

            new_height = self.driver.execute_script("return arguments[0].scrollHeight", ele)

            print(f'new height: {new_height}')
            
            if n_results:

                if number == n_results//7:
                    break

            if new_height == last_height:
                break

            print('cont')
            last_height = new_height

        #Locating the results section 

        # element = self.driver.find_element("xpath", "/html/body/div[3]/div[9]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]")
        # self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        # time.sleep(5)

        entries = self.driver.find_elements(By.CLASS_NAME, 'hfpxzc')[:-1]
        result = [] 
        
        #Extracting the information from the results  
        for entry in entries:

            place_link = entry.get_attribute('href')
            link_data = str(place_link).split('!')
            long = float([s for s in link_data if s.startswith('3d')][0][2:])
            lat = float([s for s in link_data if s.startswith('4d')][0][2:])

            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.driver.get(place_link)
            time.sleep(3)
            try:
                name = self.driver.find_element('xpath', '/html/body/div[3]/div[9]/div[3]/div[1]/div[1]/div[1]/div[2]/form/div[2]/div[3]/div/input[1]').get_attribute('value')
            except:
                pass

            buton = None
            adress = None

            try:
                buton = self.driver.find_element('xpath', '/html/body/div[3]/div[9]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[4]/div[1]/button')
            except:
                pass
            try:
                buton = self.driver.find_element('xpath', '/html/body/div[3]/div[9]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[5]/div[1]/button')
            except:
                pass
            if buton:
                buton.click()
                time.sleep(5)
                try:
                    adress = self.driver.find_element('xpath', '/html/body/div[3]/div[9]/div[3]/div[1]/div[2]/div/div[3]/div[1]/div[2]/div[2]/div[1]/div/input').get_attribute('aria-label')
                except:
                    pass

            place = []
            place.append(name)
            place.append(adress)
            place.append(long)
            place.append(lat)
            result.append(place)
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])

        print(len(result))
        return result
    
def main():
    
    mScraper = MapsScraper()
    print(mScraper.get_address())

if __name__ == "__main__":
    main()