from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
# undetected module adds some standard anti-bot detection protocols 
import time, base64, undetected_chromedriver as uc, os
from PIL import Image
import requests
import cv2 #for concatenating images
# local imports
from objs.scraper import Scraper


# Scraper module intended to scrape raws of Hoshi Tonde from Booklive.
# https://booklive.jp/product/index/title_id/557255/vol_no/001
# https://booklive.jp/bviewer/s/?cid=557255_001&rurl=https%3A%2F%2Fbooklive.jp%2Fproduct%2Findex%2Ftitle_id%2F557255%2Fvol_no%2F001

# canvas_selector = ".c-viewer__comic"
# navigation_selector = ".c-viewer__pager-next"
# page_container = ".c-viewer__pages"

class ScraperImpl(Scraper):
    
    def __init__(self, url):
        self.url = url
        # webdriver
        self.options = uc.ChromeOptions()
        self.options.enable_downloads = True
        self.options.add_argument("--disable-web-security")
        # self.options.add_argument("--headless")
        self.driver = uc.Chrome(options=self.options)

        self.dir = ""
        self.img_selector = "pages" #this div contains all pages, but each page has its own ID "content-p[i] where i is page #"
        self.page_turn_selector = "c-viewer__pager-next"

        self.selector_to_wait_for = "c-viewer__pager-next"

        # logins havent been necessary so far
        self.login_btn_selector = "" 
        self.username_field_selector = ""
        self.password_field_selector = ""
        self.enter_login_info_selector = ""

        self.images: list = []
        
    def load_page(self):
        print(f"Opening {self.url}...")
        self.driver.get(self.url)

        # wait until page content is actually loaded
        pages_present = expected_conditions.element_to_be_clickable((By.CLASS_NAME,self.img_selector)) # TODO catch wait errors for bad links
        timeout = 10 # seconds to wait until timeout
        WebDriverWait(self.driver, timeout).until(pages_present)
        time.sleep(5) # had to add 5 seconds after pages present to catch everything. Jank but highly functional for now

    # logins havent been necessary so far
    def login(self):
        return True

    def get_pages(self):
        all_loaded_pages = self.driver.find_element(By.CLASS_NAME,self.img_selector).find_elements(By.XPATH,"*")
        print("-> Images detected.")

        print("Beginning scrape...")
        os.makedirs(os.path.dirname(f"{self.dir}/"), exist_ok=True)
        try:
            for i, page in enumerate(all_loaded_pages):
                all_loaded_pages = self.driver.find_element(By.CLASS_NAME,self.img_selector).find_elements(By.XPATH,"*")
                page_container_string = f"content-p{i+1}" #page at this location is still divided into 3 parts, will need to stream together

                page_container = self.driver.find_element(By.ID,page_container_string).find_element(By.CLASS_NAME,"pt-img")
                page_data_parts = []
                page_parts = page_container.find_elements(By.XPATH,"*") #the 3 parts
                for part in page_parts:
                    part = part.find_element(By.CSS_SELECTOR,"img")
                    url = part.get_attribute("src")
                    
                    time.sleep(10)
                    break



                #combine 3 parts together with cv2
                final_image = cv2.vconcat([part for part in page_data_parts])
                self.images.append(final_image)
                time.sleep(1)
                pass
                break
                
        # try:
        # # get images, loop runs until elem without canvas is reached

        #     for i, page in enumerate(all_pages):
        #         all_pages = self.driver.find_elements(By.CLASS_NAME,self.img_selector) # needs to be updated each time
        #         canvas_element = ""
        #         # end of chapter has pages without canvas, use those to break loop
        #         try:
        #             canvas_element = page.find_element(By.TAG_NAME,"canvas")
        #         except NoSuchElementException:
        #                 print("\nEnd of chapter found, breaking loop")
        #                 break
        #         canvas_base64 = self.driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);",canvas_element)
        #         print(f"Got {i + 1} image{"" if i == 0 else "s"}...",end="\r")
        #         canvas_png = base64.b64decode(canvas_base64)
        #         self.images.append(canvas_png)

        #         # click forward a page
        #         if i % 2 == 0:
        #             next_page = self.driver.find_element(By.CLASS_NAME,self.page_turn_selector)
        #             next_page.click()
        #             time.sleep(0.1)

            self.driver.quit()
            
        except Exception as e:
            print(f"\nAn error was caught during scraping:\n{e}\nAborting")

 
    def save_pages(self):
        if len(self.images) > 0:
            for id, img in enumerate(self.images):
                print(f"Saving {id + 1}.png...",end="\r")
                with open(f"{self.dir}/page_{id + 1}.png","wb") as f:
                    f.write(img)
        print(f"\nImages saved to local directory '{self.dir}/'.")