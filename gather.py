from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException
from twitter_scraper_selenium import get_profile_details #uses  twiitter-scraper-selenium project from github
import inspect
import re
from datetime import datetime as dt
from datetime import timedelta
import time

def construct_search_term(query, hashtag = '', language = 'fr', filter_replies = True, filter_links = True, min_likes = 0, min_faves = 0, min_retweets = 0, from_date = '', until_date = '' ):
    #NOTE: dates MUST be formatted as YYYY-MM-DD str
    #all above are default for twitter filters except language
    url = 'https://twitter.com/search?q='
    url+= query +' '
    if (hashtag != ''):#can only handle a single hashtag for now
        url += '(%23'+hastags+')' + ' '
    if (language != ''):
        url += 'lang%3A'+ language + ' '
    if (filter_replies == False):
        url+='-filter%3Areplies' + ' '
    if (filter_links == False):
        url+='-filter%3Alinks' +  ' '
    url += 'min_replies%3A' + str(min_likes) +' '
    url +=  'min_faves%3A'+ str(min_faves)+' '
    url += 'min_retweets%3A' + str(min_retweets) + ' '
    if (from_date != ''):
        url += ' since%3A' + str(from_date) +' '
    if (until_date != ''):
        url += ' until%3A' + str(until_date) +' '
    url = url[:-1] #removes last un-needed whitepsace
    url += '&src=typed_query'
    return url #final twitter search url


class Scraper:

    def get_user_detail(username):
        twitter_username = "TwitterAPI"
        filename = "twitter_api_data"
        browser = "firefox"
        headless = True

    def __init__(self, webdriver_instance, page_url = ''): #placeholder
        self.driver = webdriver_instance
        #scraped data repository (assorted by index)
        #twitter '@' handle of user
        self.handles = []
        #username of user
        self.usernames = []
        #tweet text
        self.tweets = [] #tweet text
        #alphanumeric date/time of tweet
        self.dates = []
        #raw user info data and other misc
        self.raw = []
        #self

    def __scrape_current__(self):
        #temp repositories for output of method
        self.usernames_temp = []
        self.handles_temp = []
        self.dates_temp = []
        self.tweets_temp = []
        self.raw_temp = []

        #find all tweet bodies on current VISIBLE webpage. NOTE: only fetches the visible/topmost elements on page, will need to scroll down for more results as twitter displays new tweets while scrolling
        #self c1 = self.driver.find_element(by=By.XPATH, value="//div[contains(text(), 'views')]")
        raw_scrape_users = self.driver.find_elements(by=By.XPATH, value="//div[contains(@data-testid, 'User-Name')]") #all user-related info
        raw_scrape_tweets = self.driver.find_elements(by=By.XPATH, value="//div[contains(@data-testid, 'tweetText')]") #associated tweet text (same length as user info)


        for ID in raw_scrape_users: #cleaning user info

            raw_info = ID.text #ex format: 'Cultiver Son Jardin Digital\n@Graine_Digitale\n·\n9h'
            self.raw_temp.append(raw_info)
            try:
            #USER

                username = re.findall(".+?(?=\\n@)", raw_info)[0] #finds username in string
                raw_info = raw_info.replace(username, '')
                self.usernames_temp.append(username)
            except: #most likely because username is emoji
                self.usernames_temp.append('NA')

            try:
                handle = re.findall("[@]\w+",raw_info)[0] #finds twitter '@' handle in string
                self.handles_temp.append(handle)
                raw_info = raw_info.replace(handle,'')
            except:
                self.handles_temp.append('@NA')
                #print(raw_info)
            #removing excess characters
            raw_info = raw_info.replace('\n','')
            raw_info = raw_info.replace('|','')
            raw_info = raw_info.replace('·','')


            try:
                # DATE warning: not standard datetime format, four possible cases
                # CASE 1: very new tweet (<1h)
                if (type(re.search("[0-9]{1,2}[m]",raw_info) is re.Match)): #tweet date of format "XXm"
                    tweet_age = int(re.findall("[0-9]{1,2}[m]",raw_info)[0][:-1]) #extract tweet age in minutes
                    tweet_tstamp = dt.now() - time(minutes = tweet_age) #mainly checking if tweet is from today
                    self.dates_temp.append(tweet_tstamp.date())
                # CASE 2: new (1-24h) tweet
                elif (type(re.search("[0-9]{1,2}[h]",raw_info) is re.Match)): #tweet date of format "XXh"
                    tweet_age = int(re.findall("[0-9]{1,2}[h]",raw_info)[0][:-1]) #extract tweet age in minutes

                    tweet_tstamp = dt.now() - time(hours = tweet_age) #mainly checking if tweet is from today
                    self.dates_temp.append(tweet_tstamp.date())
                #CASE 3: old tweet from current year
                elif(type(re.search("[a-zA-Z]{3}[\s][0-9]{1,2}$",raw_info) is re.Match)): # date of format ex: Oct 30 [endl] (no year)

                    tweet_tstamp = dt.strptime(f"{raw_info+' '}{datetime.now().year}", "%b %d %Y") #converts twitter timestamp to  datetime format
                    self.dates_temp.append(tweet_tstamp)
                #CASE 4: really old tweet (previous year)
                elif(type(re.search("[a-zA-Z]{3}[\s][0-9]{1,2}[,][\s][0-9]{4}",raw_info) is re.Match)): # date of format ex: Oct 30, 2022

                    tweet_tstamp = dt.strptime(f"{raw_info.replace(',',' ')}", "%b %d %Y") #converts twitter timestamp to  datetime format
                    self.dates_temp.append(tweet_tstamp)
                else: #error with timestamp/invalid timestamp

                    self.dates_temp.append(raw_info)
            except:
                #ERROR, filling in with default/placeholder date
                #print(raw_info)
                self.dates_temp.append(raw_info)
        for txt in raw_scrape_tweets: #extract text body
            tweet_txt = txt.text
            self.tweets_temp.append(tweet_txt)
            #print(txt.text)
            #print("\n ##### \n")

    def __scrub__(self): #sometimes tweets aren't linked to users or users aren't linked to tweets (age source not entirely loaded?). Removes unattributed tweets/usernames
        #ALL OF THESE SHOULD MATCH, otherwise we remove excess unnatributed
        tweet_count = len(self.tweets_temp)
        user_count = len(self.usernames_temp)
        handle_count = len(self.handles_temp)
        date_count = len(self.dates_temp)
        if ((handle_count != user_count) or (user_count !=date_count)): #trivial, should theoretically always be of same length
            min_length = min(user_count, handle_count)
            self.usernames_temp = self.usernames_temp[:min_length]
            self.handles_temp = self.handles_temp[:min_length]
            self.dates_temp = self.dates_temp[:min_length]
            self.raw_temp = self.raw_temp[:min_length]
        if (user_count != tweet_count): #probable, need to check for unnatributed values
            #print("length mismatch")
            min_length = min(user_count, tweet_count)
            self.usernames_temp = self.usernames_temp[:min_length]
            self.handles_temp = self.handles_temp[:min_length]
            self.tweets_temp = self.tweets_temp[:min_length]
            self.dates_temp = self.dates_temp[:min_length]
            self.raw_temp = self.raw_temp[:min_length]

    def __archive_new__(self): #takes unique new data and stores it. Assumes that __scrub__ has been used previously

        nbr_elems = len(self.tweets_temp)
        if (nbr_elems): #null/no result
            pass
        i = 0
        while (i < nbr_elems): #iterate through new collected data (tweets/handles/usernames/dates):

            tweet = self.tweets_temp[i]
            if tweet in self.tweets: #assumes that tweets (not usernames/dates/handles) cannot be exact copies. Use of __scrub__ makes sure tweet/username/handle/date correpond and are ordered
                self.tweets_temp.pop(i)
                self.usernames_temp.pop(i)
                self.handles_temp.pop(i)
                self.dates_temp.pop(i)
                self.raw_temp.pop(i)
                nbr_elems -= 1
            else:
                i += 1
    #now that duplicates have been removed, can store original content
        self.tweets += self.tweets_temp
        self.usernames += self.usernames_temp
        self.dates += self.dates_temp
        self.handles += self.handles_temp
        self.raw += self.raw_temp





    def data_acquisition(self, tweet_target = 40, url = ''): # gets N tweets from the specified page, placeholder values
        self.driver.get(url) #REPLACE WITH URL LATER, PLACEHOLDER
        print("currently scraping: "+ url + '\n')
        self.driver.implicitly_wait(10)
        self.__scrape_current__() #gets first few tweets
        self.__scrub__() #removes fluff
        self.__archive_new__()
        current_count = len(self.tweets)
        while(current_count < tweet_target): #scrape until you have enough tweets
            print('currently scraped: ' + str(current_count))
            self.driver.execute_script('window.scrollBy(0, 2000)') #scroll down page by pixel amount. NOTE: more pixels is potentially faster but risks skipping content
            time.sleep(1)
            try:
                self.__scrape_current__() #get more tweets
                self.__scrub__() #remove unlinked elements
                self.__archive_new__() #only keep new elements
            except:
                time.sleep(2)
            current_count = len(self.tweets)




       # self.driver.execute_script('window.scrollBy(0, 2000)')



