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

#  ~ this is gonna be a lot uglier than the kowloon scraper module ~

# No matter what, I'm going to have to simulate flipping pages to access all of the pages in each chapter. 
# canvas_selector = ".c-viewer__comic"
# navigation_selector = ".c-viewer__pager-next"
# page_container = ".c-viewer__pages"

scrape_config = ScrapeConfig("ciao-nanoscrape","c-viewer__comic")
scrape_config.from_args() # get command line arguments

options = uc.ChromeOptions()
options.add_argument("--disable-web-security")
# options.set_preference("security.mixed_content.block_display_content",True)
# options.set_preference("browser.ssl_override_behavior",2)

    # browser.ssl_override_behavior = 2

    # browser.xul.error_pages.expert_bad_cert = false

    # security.ssl.errorReporting.enabled = false

# options.add_argument("--headless")
# add options here, preferably from scrape_config
driver = uc.Chrome(options=options)
images: list = []
driver.get(scrape_config.url)

# wait until page content is actually loaded
pages_present = expected_conditions.element_to_be_clickable((By.CLASS_NAME,"c-viewer__pager-next"))
timeout = 10 # seconds to wait until timeout
WebDriverWait(driver, timeout).until(pages_present)
time.sleep(5) # had to add 5 seconds after pages present to catch everything

#count number of pages
all_pages = driver.find_elements(By.CLASS_NAME,scrape_config.image_selector)
print(len(all_pages))

# to store images
scrape_config.make_directory()
try:
# get images
    for i in range(0, len(all_pages)):
        all_pages = driver.find_elements(By.CLASS_NAME,scrape_config.image_selector) # needs to be updated each time
        canvas_element = ""

        # end of chapter has pages without canvas, use those to break loop
        try:
            canvas_element = all_pages[i].find_element(By.TAG_NAME,"canvas")
        except NoSuchElementException:
                print("End of chapter found, breaking loop")
                break
        canvas_base64 = driver.execute_script("return arguments[0].toDataURL('image/png',quality=1).substring(21);",canvas_element)
        print(f"Found image {i + 1}...")
        canvas_png = base64.b64decode(canvas_base64)
        images.append(canvas_png)

        # click forward a page
        if i % 2 == 0:
            next_page = driver.find_element(By.CLASS_NAME,"c-viewer__pager-next")
            next_page.click()
    
except Exception as e:
    print(f"\nAn error was caught during scraping:\n{e}\nAborting")
finally:
    driver.quit()
    for id, img in enumerate(images):
        print(f"Saving {id + 1}.png...")
        with open(f"{scrape_config.directory}/{id + 1}.png","wb") as f:
            f.write(img)

    print("--Script complete--")