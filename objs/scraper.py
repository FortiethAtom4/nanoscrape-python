from abc import ABC, abstractmethod
import undetected_chromedriver as uc

# Absract scraper class
class Scraper(ABC):

    def __init__(self,url):
        self.url = url
        

        # for loading the webpage
        self.options: uc.ChromeOptions = None
        self.driver: uc.Chrome = None

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

    @abstractmethod
    def load_page(self):
        pass

    @abstractmethod
    def login(self):
        pass

    @abstractmethod
    def get_pages(self):
        pass

    @abstractmethod
    def save_pages(self):
        pass