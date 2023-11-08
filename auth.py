from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException
import os
import inspect
import time

#récuperer le chemin du fichier actuel pour pouvoir importer d'autres fichiers/methodes (os.getcwd ne convient pas)
script_path = (inspect.getfile(lambda: None)).rsplit('\\',1)[0]
os.chdir(script_path)
import gather


# Init navigateur
driver = webdriver.Firefox()

driver.get("https://twitter.com/search?q=chatgpt%20lang%3Afr%20-filter%3Alinks%20-filter%3Areplies&src=typed_query")

driver.implicitly_wait(10)

# Authentification

#  Complétion de l'email
text_input = driver.find_element(
    by=By.CSS_SELECTOR, value="input[autocomplete='username']")
ActionChains(driver)\
    .send_keys_to_element(text_input, "isabelle.massinon@etu.utc.fr")\
    .perform()
time.sleep(2) #delai pour eviter soucis liés à la connection

# Appui sur le bouton Suivant
try:
    next_button = driver.find_element(
    by=By.XPATH, value="//span[contains(text(), 'Suivant')]"
    )
except NoSuchElementException: #ATTENTION: text pas forcement en français, cas où text en anglais (bouton "Next")
    next_button = driver.find_element(
    by=By.XPATH, value="//span[contains(text(), 'Next')]"
    )
ActionChains(driver)\
    .click(next_button)\
    .perform()
time.sleep(1) #delai pour eviter soucis liés à la connection

#  Complétion du username
text_input = driver.find_element(
    by=By.CSS_SELECTOR, value="input[data-testid='ocfEnterTextTextInput']")
ActionChains(driver)\
    .send_keys_to_element(text_input, "CCinques59752")\
    .perform()
time.sleep(1) #delai pour eviter soucis liés à la connection
# Appui sur le bouton Suivant
try:
    next_button = driver.find_element(
    by=By.XPATH, value="//span[contains(text(), 'Suivant')]"
    )
except NoSuchElementException: #ATTENTION: text pas forcement en français, cas où text en anglais (bouton "Next")
    next_button = driver.find_element(
    by=By.XPATH, value="//span[contains(text(), 'Next')]"
)
ActionChains(driver)\
    .click(next_button)\
    .perform()
time.sleep(2) #delai pour eviter soucis liés à la connection

#Complétion mot de passe
password_input = driver.find_element(
    by=By.NAME, value="password"
)
ActionChains(driver)\
    .send_keys_to_element(password_input, "IC05*Twitter")\
    .perform()
time.sleep(1) #delai pour eviter soucis liés à la connection

#Appui sur le bouton Se Connecter
try:
    login_button = driver.find_element(
    by=By.XPATH, value="//span[contains(text(), 'Se connecter')]"
    )
except NoSuchElementException: #cas text anglais
    login_button = driver.find_element(
    by=By.XPATH, value="//span[contains(text(), 'Log in')]")
time.sleep(1) #delai pour eviter soucis liés à la connection

ActionChains(driver)\
    .click(login_button)\
    .perform()
time.sleep(2) #delai pour eviter soucis liés à la connection

#recuperation du texte relatif à la requete (prototype/test)
scraper = gather.Scraper(driver)
url_search = gather.construct_search_term('chatgpt', filter_links = False, filter_replies = False)
#scraper.scroll_until_count(20)
scraper.data_acquisition(url = url_search)

