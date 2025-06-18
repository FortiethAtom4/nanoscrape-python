from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
# undetected module adds some standard anti-bot detection protocols 
import time, base64, undetected_chromedriver as uc, maskpass, os

# local imports
from objs.scraper import Scraper


# Scraper module intended to scrape raws from youngchampion.
# Example link: https://youngchampion.jp/episodes/32d1bb62782b8/


# current chapter to get: 19 https://youngchampion.jp/episodes/992fa25877712/

# canvas_selector = "-cv-page-canvas" -> 1st child is the canvas element
# navigation_selector = ".-cv-nav mode-l"
# page_container = ".cv-page"

# last page selector: "#xCVLastPage"

class ScraperImpl(Scraper):

    def __init__(self,url):
        self.url = url
        # webdriver
        self.options = uc.ChromeOptions()
        self.options.add_argument("--disable-web-security")
        self.options.add_argument("--headless")
        self.driver = uc.Chrome(options=self.options)

        self.dir = ""
        self.img_selector = "-cv-page-canvas"
        self.page_turn_selector = "mode-l"

        self.selector_to_wait_for = "-cv-inst-btn"

        # how nice of them to use unique IDs to make this much easier
        self.login_btn_selector = "login-popup-login-btn" 
        self.username_field_selector = "input.form-control:nth-child(2)"
        self.password_field_selector = "#password"
        self.enter_login_info_selector = "#btn-login"

        self.images: list = []


    def get_pages(self):
        # wait until page content is actually loaded
        pages_present = expected_conditions.element_to_be_clickable((By.CLASS_NAME,self.selector_to_wait_for)) # TODO catch wait errors for bad links
        timeout = 10 # seconds to wait until timeout
        WebDriverWait(self.driver, timeout).until(pages_present)

        help_window_close_button = self.driver.find_element(By.CLASS_NAME,self.selector_to_wait_for)
        help_window_close_button.click()

        time.sleep(5) # had to add 5 seconds after pages present to catch everything. Jank but highly functional for now

        #count number of pages
        all_pages = self.driver.find_elements(By.CLASS_NAME,self.img_selector)

        print(f"-> {len(all_pages)} images detected.")

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
                        # print("\nEnd of chapter found, breaking loop")
                        continue
                canvas_base64 = self.driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);",canvas_element)
                print(f"Got {i + 1} image{"" if i == 0 else "s"}...",end="\r")
                canvas_png = base64.b64decode(canvas_base64)
                self.images.append(canvas_png)

                # click forward a page
                if i % 2 == 0:
                    next_page = self.driver.find_element(By.CLASS_NAME,self.page_turn_selector)
                    next_page.click()
                    time.sleep(0.5)
            
        except Exception as e:
            print(f"\nAn error was caught during scraping:\n{e}\nAborting")