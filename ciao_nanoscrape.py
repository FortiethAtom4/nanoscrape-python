from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
import requests

# local imports
from objs.scrape_config import ScrapeConfig


# Scraper module intended to scrape raws of NekoMeru from Ciao.
# Example link: https://ciao.shogakukan.co.jp/comics/title/00511/episode/20257 

#  ~ this is gonna be a lot uglier than the kowloon scraper module ~

# No matter what, I'm going to have to simulate flipping pages to access all of the pages in each chapter. 
# canvas_selector = ".c-viewer__comic"
# navigation_selector = ".c-viewer__pager-next"
# page_container = ".c-viewer__pages"

scrape_config = ScrapeConfig("nekomeru-nanoscrape","c-viewer__comic")
scrape_config.from_args() # get command line arguments

options = Options()
# options.add_argument("--headless")
# add options here, preferably from scrape_config

try:
    driver = webdriver.Firefox(options=options)
    driver.get(scrape_config.url)

    # wait until page content is actually loaded
    pages_present = expected_conditions.presence_of_all_elements_located((By.CLASS_NAME,scrape_config.image_selector))
    timeout = 10 # seconds to wait until timeout
    WebDriverWait(driver, timeout).until(pages_present)
    
    
    # to store images
    images: set = {}

# TODO

    driver.quit()


except Exception as e:
    print(f"\nAn error was caught during scraping:\n{e}\nAborting")
finally:
    print("--Script complete--")