from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains


# Init navigateur
driver = webdriver.Firefox()

driver.get("https://twitter.com/search?q=chatgpt%20lang%3Afr%20-filter%3Alinks%20-filter%3Areplies&src=typed_query")
driver.implicitly_wait(5)

# Authentification

#  Complétion de l'email
text_input = driver.find_element(
    by=By.CSS_SELECTOR, value="input[autocomplete='username']")
ActionChains(driver)\
    .send_keys_to_element(text_input, "isabelle.massinon@etu.utc.fr")\
    .perform()

# Appui sur le bouton Suivant
next_button = driver.find_element(
    by=By.XPATH, value="//span[contains(text(), 'Suivant')]"
)
ActionChains(driver)\
    .click(next_button)\
    .perform()


#  Complétion du username
text_input = driver.find_element(
    by=By.CSS_SELECTOR, value="input[data-testid='ocfEnterTextTextInput']")
ActionChains(driver)\
    .send_keys_to_element(text_input, "CCinques59752")\
    .perform()

# Appui sur le bouton Suivant
next_button = driver.find_element(
    by=By.XPATH, value="//span[contains(text(), 'Suivant')]"
)
ActionChains(driver)\
    .click(next_button)\
    .perform()


#Complétion mot de passe
password_input = driver.find_element(
    by=By.NAME, value="password"
)
ActionChains(driver)\
    .send_keys_to_element(password_input, "IC05*Twitter")\
    .perform()

#Appui sur le bouton Se Connecter
login_button = driver.find_element(
    by=By.XPATH, value="//span[contains(text(), 'Se connecter')]"
)
ActionChains(driver)\
    .click(login_button)\
    .perform()

