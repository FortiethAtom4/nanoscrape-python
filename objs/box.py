import time, os, maskpass
import selenium.webdriver as uc 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from objs.scraper import Scraper
from selenium_stealth import stealth

class ScraperImpl(Scraper):

    def __init__(self,url):
        self.url = url

        # for loading the webpage
        
        self.options = uc.ChromeOptions()
        self.options.add_argument("--disable-web-security")
        self.options.add_argument("--log-level=1")
        # self.options.add_argument("--headless=new")
        self.driver = uc.Chrome(options=self.options)

        stealth(self.driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )

        self.dir = ""
        self.img_selector = ""
        self.page_turn_selector = ".Pagination__DesktopWrapper-sc-1oq4naf-4 > div:nth-child(1) > a:nth-child(7)"

        # wait for this selector to load before starting scrape. Usually same as img_selector but not necessarily.
        self.selector_to_wait_for = "div.LazyImage__BgImage-sc-14k46gk-3:nth-child(2)"
        # CommonButton__CommonButtonInner-sc-1s35wwu-2 ioTSpN

        # .LazyImage__BgImage-sc-14k46gk-3"

        # login field selectors. Only required if login requested.
        self.login_btn_selector = "button.flNDpw:nth-child(1) > div:nth-child(1)" # if this button is detected, then login is usually required.
        self.username_field_selector = "fieldset.sc-bn9ph6-0:nth-child(2) > label:nth-child(1) > input:nth-child(1)"
        self.password_field_selector = "fieldset.sc-bn9ph6-0:nth-child(3) > label:nth-child(1) > input:nth-child(1)"
        self.enter_login_info_selector = "button.charcoal-button:nth-child(4)"

        # specific to this site

        # posts have this class
        self.all_posts_selector = ".CreatorPostList__CardsWrapper-sc-1gerkjf-2"
        self.post_selector = ".CardPostItem__Wrapper-sc-1bjj922-0 .eGwQXQ"

        # images in post are under this 
        self.images_wrapper = ".styled__Wrapper-sc-1vjtieq-0 > article:nth-child(1)"


        self.post_pages_selector = ".Pagination__DesktopWrapper-sc-1oq4naf-4 > div:nth-child(1)"
        

        self.images: list = []

    def load_page(self):
        print(f"Opening {self.url}...")
        try:
            self.driver.get(self.url)
            pages_present = expected_conditions.element_to_be_clickable((By.CSS_SELECTOR,self.selector_to_wait_for))

            timeout = 10 # seconds to wait until timeout
            WebDriverWait(self.driver, timeout).until(pages_present)

            age_button = self.driver.find_element(By.CSS_SELECTOR,self.selector_to_wait_for)
            age_button.click()
        except:
            print("Warning: Wait timeout reached.")
        time.sleep(5)

    # not all sites will need this function
    def login(self, username, password):
        print("Login phase started...")
        login_button = ""
        try:
            login_button = self.driver.find_element(By.CSS_SELECTOR,self.login_btn_selector)
        except NoSuchElementException:
            print("login button not detected, skipping")
            return True
        
        try:
            print("Login requested")
            login_button.click()
            time.sleep(2)


            rental_username = self.driver.find_element(By.CSS_SELECTOR,self.username_field_selector)
            if username == None:
                username = input("Enter username: ")
            rental_username.send_keys(username)

            rental_password = self.driver.find_element(By.CSS_SELECTOR,self.password_field_selector)
            if password == None:
                password = maskpass.askpass(prompt="Enter password: ",mask="*")
            rental_password.send_keys(password)

            login_enter_button = self.driver.find_element(By.CSS_SELECTOR,self.enter_login_info_selector)
            login_enter_button.click()
        except:
            return False
        time.sleep(5)
        return True

    def get_pages(self):
        # get num of pages of posts first
        pages_to_turn = True

        while pages_to_turn:
            post_wrapper = self.driver.find_element(By.CSS_SELECTOR,self.all_posts_selector)

            all_posts_on_page = self.driver.find_elements(By.CSS_SELECTOR,self.post_selector)

            for post in all_posts_on_page:
                post.click()
                pages_present = expected_conditions.element_to_be_clickable((By.CSS_SELECTOR,self.selector_to_wait_for))
                timeout = 5 # seconds to wait until timeout
                WebDriverWait(self.driver, timeout).until(pages_present)

            # no more pages, call it
            try:
                page_turn_button = self.driver.find_element(By.CSS_SELECTOR,self.page_turn_selector)
            except:
                pages_to_turn = False

    def save_pages(self):
        if len(self.images) > 0:
            os.makedirs(os.path.dirname(f"{self.dir}/"), exist_ok=True)
            for id, img in enumerate(self.images):
                print(f"Saving {id + 1}.png...",end="\r")
                with open(f"{self.dir}/page_{id + 1}.png","wb") as f:
                    f.write(img)
            print(f"\nImages saved to local directory '{self.dir}/'.")
        else:
            print("\nWarning: no images to save.")