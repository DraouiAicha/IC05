from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException
import inspect
import re
from datetime import datetime as dt
from datetime import timedelta



class Scraper:


    def __init__(self, webdriver_instance, page_url = ''): #placeholder
        self.driver = webdriver_instance
        #scraped data repository (assorted by index)
        self.handle = [] #twitter '@' handle of user
        self.username = []
        self.tweets = [] #tweet text
        self.date = [] #alphanumeric date/time of tweet

    def scroll_until_count(self, tweet_target = 10): #scrolls twitter feed until enough tweets are loaded (assumed tweets stay loaded)!Currently not working!
        #current_depth = 10000;
        current_tweet_count = 0;
        past_tweet_count = -1 #checking in case old tweets are being deleted
        while((current_tweet_count < tweet_target) and (past_tweet_count < current_tweet_count)): #keeps scrolling as long as enough tweets haven't loaded
            past_tweet_count = current_tweet_count
            raw_scrape_users = self.driver.find_elements(by=By.XPATH, value="//div[contains(@data-testid, 'User-Name')]") #used to check number of loaded tweets
            current_tweet_count = len(raw_scrape_users)
            self.driver.execute_script("window.scrollTo(0, window.scrollY + 10000)") #scroll down page
            #current_depth += 10000
            print("scrolling")
        self.tweet_count = current_tweet_count


    def scrape_text(self):
        #find all tweet bodies on current webpage. NOTE: only fetches the visible/topmost elements on page, will need to scroll down for more results as twitter displays new tweets while scrolling
        raw_scrape_users = self.driver.find_elements(by=By.XPATH, value="//div[contains(@data-testid, 'User-Name')]") #all user-related info
        raw_scrape_tweets = self.driver.find_elements(by=By.XPATH, value="//div[contains(@data-testid, 'tweetText')]") #associated tweet text (same length as user info)

        for ID in raw_scrape_users: #cleaning user info
            raw_info = ID.text #ex format: 'Cultiver Son Jardin Digital\n@Graine_Digitale\n·\n9h'
            raw_info = raw_info.split('\n')

            #USER
            self.handle.append(raw_info[1])
            self.username.append(raw_info[0])
            try:
                # DATE warning: not standard datetime format, four possible cases
                # CASE 1: very new tweet (<1h)
                if (type(re.search("[0-9]{1,2}[m]",raw_info[-1]) is re.Match)): #tweet date of format "XXm"
                    tweet_age = int(re.search("[0-9]{1,2}[m]",raw_info[-1]).string[:-1]) #extract tweet age in minutes
                    tweet_tstamp = dt.now() - time(minutes = tweet_age) #mainly checking if tweet is from today
                    self.date.append(tweet_tstamp.date())
                # CASE 2: new (1-24h) tweet
                elif (type(re.search("[0-9]{1,2}[h]",raw_info[-1]) is re.Match)): #tweet date of format "XXh"
                    tweet_age = int(re.search("[0-9]{1,2}[m]",raw_info[-1]).string[:-1]) #extract tweet age in hours
                    tweet_tstamp = dt.now() - time(hours = tweet_age) #mainly checking if tweet is from today
                    self.date.append(tweet_tstamp.date())
                #CASE 3: old tweet from current year
                elif(type(re.search("[a-zA-Z]{3}[\s][0-9]{1,2}$",raw_info[-1]) is re.Match)): # date of format ex: Oct 30 [endl] (no year)
                    tweet_tstamp = dt.strptime(f"{raw_info[-1]+' '}{datetime.now().year}", "%b %d %Y") #converts twitter timestamp to  datetime format
                    self.date.append(tweet_tstamp)
                #CASE 4: really old tweet (previous year)
                elif(type(re.search("[a-zA-Z]{3}[\s][0-9]{1,2}[,][\s][0-9]{4}",raw_info[-1]) is re.Match)): # date of format ex: Oct 30, 2022
                    tweet_tstamp = dt.strptime(f"{raw_info[-1].replace(',',' ')}", "%b %d %Y") #converts twitter timestamp to  datetime format
                    self.date.append(tweet_tstamp)
                else: #error with timestamp/invalid timestamp
                    self.date.append(raw_info[-1])
            except:
                #ERROR, filling in with default/placeholder date
                self.date.append(dt(1970,1,1))
    for txt in raw_scrape_tweets: #extract text body
            tweet_txt = txt.text
            self.tweets.append(tweet_txt)



