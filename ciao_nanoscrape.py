from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
# undetected module adds some standard anti-bot detection protocols 
import requests, time, base64, undetected_chromedriver as uc

# local imports
from objs.scrape_config import ScrapeConfig


# Scraper module intended to scrape raws of NekoMeru from Ciao.
# Example link: https://ciao.shogakukan.co.jp/comics/title/00511/episode/27493

# canvas_selector = ".c-viewer__comic"
# navigation_selector = ".c-viewer__pager-next"
# page_container = ".c-viewer__pages"

scrape_config = ScrapeConfig("ciao-nanoscrape","c-viewer__comic")
scrape_config.from_args() # get command line arguments


options = uc.ChromeOptions()
options.add_argument("--disable-web-security")
options.add_argument("--headless")
# add options here, preferably from scrape_config
driver = uc.Chrome(options=options)
images: list = []

print(f"Opening {scrape_config.url}...")
driver.get(scrape_config.url)

# wait until page content is actually loaded
pages_present = expected_conditions.element_to_be_clickable((By.CLASS_NAME,"c-viewer__pager-next")) # TODO catch wait errors for bad links
timeout = 10 # seconds to wait until timeout
WebDriverWait(driver, timeout).until(pages_present)
time.sleep(5) # had to add 5 seconds after pages present to catch everything. Jank but highly functional for now

#count number of pages
all_pages = driver.find_elements(By.CLASS_NAME,scrape_config.image_selector)
print("-> Images detected.")

print("Beginning scrape...")
scrape_config.make_directory() 
try:
# get images, loop runs until elem without canvas is reached
    for i, page in enumerate(all_pages):
        all_pages = driver.find_elements(By.CLASS_NAME,scrape_config.image_selector) # needs to be updated each time
        canvas_element = ""

        # end of chapter has pages without canvas, use those to break loop
        try:
            canvas_element = page.find_element(By.TAG_NAME,"canvas")
        except NoSuchElementException:
                print("\nEnd of chapter found, breaking loop")
                break
        canvas_base64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);",canvas_element)
        print(f"Got {i + 1} image{"" if i == 0 else "s"}...",end="\r")
        canvas_png = base64.b64decode(canvas_base64)
        images.append(canvas_png)

        # click forward a page
        if i % 2 == 0:
            next_page = driver.find_element(By.CLASS_NAME,"c-viewer__pager-next")
            next_page.click()
            time.sleep(0.1)
    
except Exception as e:
    print(f"\nAn error was caught during scraping:\n{e}\nAborting")
finally:
    driver.close()
    if len(images) > 0:
        for id, img in enumerate(images):
            print(f"Saving {id + 1}.png...")
            with open(f"{scrape_config.directory}/{id + 1}.png","wb") as f:
                f.write(img)
        print(f"\nImages saved to local directory '{scrape_config.directory}/'.")

    print("\n--Scrape complete--\n")