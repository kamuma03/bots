from selenium import webdriver
import json
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from time import sleep, time
import random
import re
import subprocess, os
import requests

max_time = 10

class Bot():
    def __init__(self, headless=False, verbose=False):
        print('initialising bot')

        options = Options()
        options.add_argument("--no-sandbox")	# without this, the chrome webdriver can't start (SECURITY RISK)
        if headless:
            options.add_argument("--headless")
        #options.add_argument("--window-size=1920x1080")
        self.driver = webdriver.Chrome(chrome_options=options)			# create webdriver
        self.verbose = verbose

    def click_btn(self, text):
        if self.verbose: print(f'clicking {text} btn')
        element_types = ['button', 'div', 'input', 'a', 'label']
        for element_type in element_types:
            btns = self.driver.find_elements_by_xpath(f'//{element_type}')
            # for btn in btns:
            #     print(btn.text)
            
            # SEARCH BY TEXT
            try:
                btn = [b for b in btns if b.text.lower() == text.lower()][0]
                btn.click()
                return
            except IndexError:
                pass

            # SEARCH BY VALUE ATTRIBUTE IF NOT YET FOUND
            try:
                btn = self.driver.find_elements_by_xpath(f'//{element_type}[@value="{text}"]')[0]
                btn.click()
                return
            except:
                continue

        raise ValueError(f'button containing "{text}" not found')

    def _search(self, query, _type='search', placeholder=None):
        sleep(1)
        s = self.driver.find_elements_by_xpath(f'//input[@type="{_type}"]')
        print(s)
        if placeholder:
            s = [i for i in s if i.get_attribute('placeholder').lower() == placeholder.lower()][0]
        else:
            s = s[0]
        s.send_keys(query) 

    def toggle_verbose(self):
        self.verbose = not self.verbose

if __name__ == '__main__':
    # EXAMPLE USAGE
    bot = Bot()

    searaches = ['shoes', 'tops', 'pants']

    for search in searaches:
        bot.driver.get(f'https://www.depop.com/search/?q={search}')
        
        results = bot.driver.find_elements_by_xpath('//*[@id="main"]/div[2]/div/ul/li/a')
        print(f'found {len(results)} results for search "{search}"')
        results = [r.get_attribute('href') for r in results]

        for result in results:

            print(result)

            bot.driver.get(result)

            bot.driver.execute_script("window.scrollBy(0,925)", "")

            result = result.split('/')[-2]

            imgs = bot.driver.find_elements_by_xpath('//*[@id="main"]/div[1]/div[2]/div/img')
            print('# imgs: ', len(imgs))
            imgs = [i.get_attribute('src') for i in imgs]
            imgs = [i for i in imgs if i != None]

            os.makedirs(f'data/{result}', exist_ok=True)

            for idx, img_url in enumerate(imgs):
                response = requests.get(img_url)
                img_name = f'{result}-{idx}'
                file_ext = img_url.split('.')[-1]
                with open(f'data/{result}/{img_name}.{file_ext}', 'wb') as f:
                    f.write(response.content)
            
            print()