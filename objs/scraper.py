import undetected_chromedriver as uc, time, os, maskpass
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
# Absract scraper class
# TODO given the repeated code, better to make this a parent class with pre-implemented login + save than an abstract class.
class Scraper():

    def __init__(self,url):
        self.url = url

        # for loading the webpage
        self.options: uc.ChromeOptions
        self.driver: uc.Chrome

        self.dir = ""
        self.img_selector = ""
        self.page_turn_selector = ""

        # wait for this selector to load before starting scrape. Usually same as img_selector but not necessarily.
        self.selector_to_wait_for = ""

        # login field selectors. Only required if login requested.
        self.login_btn_selector = "" # if this button is detected, then login is usually required.
        self.username_field_selector = ""
        self.password_field_selector = ""
        self.enter_login_info_selector = ""

        self.images: list = []

    def load_page(self):
        print(f"Opening {self.url}...")
        self.driver.get(self.url)
        pages_present = expected_conditions.element_to_be_clickable((By.CSS_SELECTOR,self.selector_to_wait_for)) # TODO catch wait errors for bad links
        timeout = 10 # seconds to wait until timeout
        WebDriverWait(self.driver, timeout).until(pages_present)
        time.sleep(5)

    # not all sites will need this function
    def login(self, username, password):
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
            print("Login phase started...")

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

    # The meat of the scraper, to be overridden in a child class
    def get_pages(self):
        print("Warning: no implementation found.")

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