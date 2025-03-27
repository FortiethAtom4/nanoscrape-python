from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
# undetected module adds some standard anti-bot detection protocols 
import time, base64, undetected_chromedriver as uc, os

# local imports
from objs.scraper import Scraper


# Scraper module intended to scrape raws of NekoMeru from Ciao.
# Example link: https://ciao.shogakukan.co.jp/comics/title/00511/episode/27493

# canvas_selector = ".c-viewer__comic"
# navigation_selector = ".c-viewer__pager-next"
# page_container = ".c-viewer__pages"

class ScraperImpl(Scraper):
    
    def __init__(self, url):
        self.url = url
        # webdriver
        self.options = uc.ChromeOptions()
        self.options.add_argument("--disable-web-security")
        self.options.add_argument("--headless")
        self.driver = uc.Chrome(options=self.options)

        self.dir = ""
        self.img_selector = "c-viewer__comic"
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
        pages_present = expected_conditions.element_to_be_clickable((By.CLASS_NAME,self.page_turn_selector)) # TODO catch wait errors for bad links
        timeout = 10 # seconds to wait until timeout
        WebDriverWait(self.driver, timeout).until(pages_present)
        time.sleep(5) # had to add 5 seconds after pages present to catch everything. Jank but highly functional for now

    # logins havent been necessary so far
    def login(self):
        return True

    def get_pages(self):
        all_pages = self.driver.find_elements(By.CLASS_NAME,self.img_selector)
        print("-> Images detected.")

        print("Beginning scrape...")
        os.makedirs(os.path.dirname(f"{self.dir}/"), exist_ok=True)
        try:
        # get images, loop runs until elem without canvas is reached
            for i, page in enumerate(all_pages):
                all_pages = self.driver.find_elements(By.CLASS_NAME,self.img_selector) # needs to be updated each time
                canvas_element = ""
                # end of chapter has pages without canvas, use those to break loop
                try:
                    canvas_element = page.find_element(By.TAG_NAME,"canvas")
                except NoSuchElementException:
                        print("\nEnd of chapter found, breaking loop")
                        break
                canvas_base64 = self.driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);",canvas_element)
                print(f"Got {i + 1} image{"" if i == 0 else "s"}...",end="\r")
                canvas_png = base64.b64decode(canvas_base64)
                self.images.append(canvas_png)

                # click forward a page
                if i % 2 == 0:
                    next_page = self.driver.find_element(By.CLASS_NAME,self.page_turn_selector)
                    next_page.click()
                    time.sleep(0.1)

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