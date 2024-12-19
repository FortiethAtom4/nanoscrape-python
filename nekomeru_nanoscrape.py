from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import requests

# local imports
from objs.scrape_config import ScrapeConfig


# Scraper module intended to scrape raws of NekoMeru from Ciao.
# Example link: https://ciao.shogakukan.co.jp/comics/title/00511/episode/20257 

#  ~ this is gonna be a lot uglier than the kowloon scraper module ~

scrape_config = ScrapeConfig("nekomeru-nanoscrape")
scrape_config.from_args() # get command line arguments

options = Options()
# options.add_argument("--headless")
# add options here, preferably from scrape_config

try:
    driver = webdriver.Firefox(options=options)
    driver.get(scrape_config.url)
    # driver.implicitly_wait(10)
    
    # to store images
    images: set = {}

# TODO

    driver.quit()


except Exception as e:
    print(f"\nAn error was caught during scraping:\n{e}\nAborting")
finally:
    print("--Script complete--")