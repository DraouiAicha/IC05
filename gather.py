from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException
from twitter_scraper_selenium import get_profile_details #uses  twiitter-scraper-selenium project from github
import inspect
import re
from datetime import datetime
from datetime import timedelta
import time
import csv

#max number of consecutive fails allowed when scraping new data
max_try = 10

def construct_search_term(query, hashtag = '', language = 'fr', filter_replies = True, filter_links = True, min_replies = 0, min_likes = 0, min_retweets = 0, from_date = '', until_date = '' ):
    #NOTE: dates MUST be formatted as YYYY-MM-DD str
    #all above are default for twitter filters except language
    url = 'https://twitter.com/search?q='
    url+= query +' '
    if (hashtag != ''):#can only handle a single hashtag for now
        url += '(%23'+hashtag+')' + ' '
    if (language != ''):
        url += 'lang%3A'+ language + ' '
    if (filter_replies == False):
        url+='-filter%3Areplies' + ' '
    if (filter_links == False):
        url+='-filter%3Alinks' +  ' '
    url += 'min_replies%3A' + str(min_replies) +' '
    url +=  'min_faves%3A'+ str(min_likes)+' '
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
        #number of likes
        self.likes = []
        #number of retweets
        self.retweets = []
        #raw user info data and other misc
        self.raw = []
        #self

    def __parse_date__(self, date_str):
        # Define regular expressions for each date format
        month_day_regex = re.compile(r'([A-Za-z]{3})\s(\d{1,2})$')
        age_minutes_regex = re.compile(r'(\d+)m')
        age_hours_regex = re.compile(r'(\d+)h')
        full_timestamp_regex = re.compile(r'([A-Za-z]{3})\s(\d{2})\s{0,1},\s{0,1}(\d{4})')

        # Match different formats
        match_month_day = month_day_regex.match(date_str)
        match_age_minutes = age_minutes_regex.match(date_str)
        match_age_hours = age_hours_regex.match(date_str)
        match_full_timestamp = full_timestamp_regex.match(date_str)

        current_timestamp = datetime.now()

        if (match_month_day):
            # Format: Month + day
            month, day = match_month_day.groups()
            year = current_timestamp.year
            return f"{int(year):04d}-{datetime.strptime(month, '%b').month:02d}-{int(day):02d}"


        elif match_age_minutes:
            # Format: Age in minutes
            minutes = int(match_age_minutes.group(1))
            return (current_timestamp - timedelta(minutes=minutes)).strftime("%Y-%m-%d")

        elif match_age_hours:
            # Format: Age in hours
            hours = int(match_age_hours.group(1))
            return (current_timestamp - timedelta(hours=hours)).strftime("%Y-%m-%d")

        elif match_full_timestamp:
            # Format: Full timestamp
            month, day, year = match_full_timestamp.groups()
            return f"{int(year):04d}-{month}-{int(day):02d}"

        else:
            # Invalid format or other cases
            return '1970-01-01'
            #return current_timestamp.strftime("%Y-%m-%d")


    def __scrape_current__(self):
        #temp repositories for output of method
        self.usernames_temp = []
        self.handles_temp = []
        self.dates_temp = []
        self.tweets_temp = []
        self.raw_temp = []
        self.likes_temp = []
        self.retweets_temp = []

        #find all tweet bodies on current VISIBLE webpage. NOTE: only fetches the visible/topmost elements on page, will need to scroll down for more results as twitter displays new tweets while scrolling
        #self c1 = self.driver.find_element(by=By.XPATH, value="//div[contains(text(), 'views')]")
        raw_scrape_users = self.driver.find_elements(by=By.XPATH, value="//div[contains(@data-testid, 'User-Name')]") #all user-related info
        raw_scrape_tweets = self.driver.find_elements(by=By.XPATH, value="//div[contains(@data-testid, 'tweetText')]") #associated tweet text (same length as user info)
        raw_scrape_likes = self.driver.find_elements(by=By.XPATH, value="//div[contains(@data-testid, 'like')]") #associated tweet text (same length as user info)
        raw_scrape_retweets = self.driver.find_elements(by=By.XPATH, value="//div[contains(@data-testid, 'retweet')]") #associated tweet text (same length as user info)


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

            date_str = self.__parse_date__(raw_info)
            self.dates_temp.append(date_str)

        for txt in raw_scrape_tweets: #extract text body
            tweet_txt = txt.text
            self.tweets_temp.append(tweet_txt)
            #print(txt.text)
            #print("\n ##### \n")

        for like in raw_scrape_likes:
            nb_like = like.text
            if 'K' in nb_like:  #superior to 1000
                nb_like = int(float(nb_like.replace('K', '').replace('','')) * 1000)
            elif len(nb_like) < 1: #empty string
                nb_like = 0
            else:
                nb_like = int(nb_like.replace(' ',''))
            self.likes_temp.append(nb_like)

        for rt in raw_scrape_retweets:
            nb_rt = rt.text
            if 'K' in nb_rt: #superior to 1000
                nb_rt = int(float(nb_rt.replace('K', '').replace(' ','')) * 1000)
            elif len(nb_rt) < 1: #empty string
                nb_rt = 0
            else:
                nb_rt = int(nb_rt.replace(' ',''))
            self.retweets_temp.append(nb_rt)      


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
            self.likes_temp = self.likes_temp[:min_length]
            self.retweets_temp = self.retweets_temp[:min_length]
        if (user_count != tweet_count): #probable, need to check for unnatributed values
            #print("length mismatch")
            min_length = min(user_count, tweet_count)
            self.usernames_temp = self.usernames_temp[:min_length]
            self.handles_temp = self.handles_temp[:min_length]
            self.tweets_temp = self.tweets_temp[:min_length]
            self.dates_temp = self.dates_temp[:min_length]
            self.raw_temp = self.raw_temp[:min_length]
            self.likes_temp = self.likes_temp[:min_length]
            self.retweets_temp = self.retweets_temp[:min_length]

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
                self.likes_temp.pop(i)
                self.retweets_temp.pop(i)
                nbr_elems -= 1
            else:
                i += 1
    #now that duplicates have been removed, can store original content
        self.tweets += self.tweets_temp
        self.usernames += self.usernames_temp
        self.dates += self.dates_temp
        self.handles += self.handles_temp
        self.raw += self.raw_temp
        self.likes += self.likes_temp
        self.retweets += self.retweets_temp



    def data_acquisition(self, tweet_target = 40, url = ''): # gets N tweets from the specified page, placeholder values
        self.driver.get(url) #REPLACE WITH URL LATER, PLACEHOLDER
        print("currently scraping: "+ url + '\n')
        self.driver.implicitly_wait(10)
        self.__scrape_current__() #gets first few tweets
        self.__scrub__() #removes fluff
        self.__archive_new__()
        current_count = len(self.tweets)
        try_nb = 0
        while(current_count < tweet_target and try_nb < max_try): #scrape until you have enough tweets
            if try_nb > 0:
                print(str(try_nb) + ' tries (' + str(current_count)+ ' scraped)')
            else:
                print('currently scraped: ' + str(current_count))
            self.driver.execute_script('window.scrollBy(0, 2000)') #scroll down page by pixel amount. NOTE: more pixels is potentially faster but risks skipping content
            time.sleep(1.5)
            try:
                self.__scrape_current__() #get more tweets
                self.__scrub__() #remove unlinked elements
                self.__archive_new__() #only keep new elements

                # if number of tweets hasn't changed, it means no new data has been scraped, scroll didn't work
                if (current_count == len(self.tweets)):
                    try_nb += 1
                else: # if success, reset of try_nb
                    try_nb = 0
            except:
                print('failed to scrape')
                time.sleep(2)
            current_count = len(self.tweets)


    def write_tweets_to_csv(self, dest_filename, sep = ';', new_line =''):

        # Combine lists into a list of lists
        data = [self.dates, self.usernames, self.handles, self.tweets, self.likes, self.retweets]

        # Transpose the data to have lists as rows and columns as columns
        data_transposed = list(map(list, zip(*data)))

        # Add a title for each column
        header = ['Date', 'Username', 'Handle', 'Tweet body', 'Number of likes', 'Number of retweets']
        csv_format = {
            'delimiter': ',',
            'quotechar': '"',
            'quoting': csv.QUOTE_MINIMAL
        }


    # Write to CSV file with specified format
        with open(dest_filename, 'w', newline=new_line,  encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, **csv_format)
            # Write the header
            writer.writerow(header)
            # Write the data
            writer.writerows(data_transposed)


# NOT CURRENTLY WORKING

    def scrape_user_data(self, search_from_dict = False, search_other_users = False): #uses twitter handles to extract
        #for handle in self.handles[:1]:

        handle = self.handles[0]
        #if handle == '@NA':
        #        continue #if handle is invalid, go to next
        #else:
        username = handle[1:]

        user_url = 'https://twitter.com/'+username
        print(user_url)
        print(username)
        field = '/'+username+'/following'
        print(field)
        self.driver.get(user_url) #acquire web page

        self.followers_raw = self.driver.find_element( by=By.PARTIAL_LINK_TEXT, value=field)




