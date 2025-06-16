from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
# undetected module adds some standard anti-bot detection protocols 
import time, base64, undetected_chromedriver as uc, os, maskpass

# Scraper module intended to scrape raws of Kowloon Generic Romance from ShonenJumpPlus.
# Example link: https://shonenjumpplus.com/episode/17106567256754793848
# This site often requires a login and payment to scrape, so remote login will be required in order to scrape.

# pages are held in canvases with class "page-image" within <p> tags with class "page-area"

# fix for undetected-chromedriver OS error: https://stackoverflow.com/questions/74817978/oserror-winerror-6-with-undetected-chromedriver/76497142

# local imports
from objs.scraper import Scraper
# Absract scraper class
class ScraperImpl(Scraper):

    def __init__(self,url):
        self.url = url
        
        # for loading the webpage
        self.options = uc.ChromeOptions()
        self.options.add_argument("--disable-web-security")
        self.options.add_argument("--headless")
        self.driver = uc.Chrome(options=self.options)

        self.dir = ""
        self.img_selector = ".page-area"
        self.page_turn_selector = ".page-navigation-forward"

        # wait for this selector to load before starting scrape. Usually same as img_selector but not necessarily.
        self.selector_to_wait_for = ""

        # login field selectors. Only required if login requested.
        self.login_btn_selector = ".rental-button-box" # if this button is detected, then login is usually required.
        self.username_field_selector = ""
        self.password_field_selector = ""
        self.enter_login_info_selector = ""

        self.images: list = []

    def load_page(self):
        print(f"Opening {self.url}...")
        self.driver.get(self.url)
        pages_present = expected_conditions.element_to_be_clickable((By.CSS_SELECTOR,self.img_selector)) # TODO catch wait errors for bad links
        timeout = 10 # seconds to wait until timeout
        WebDriverWait(self.driver, timeout).until(pages_present)
        time.sleep(3)
        #count number of pages

    def login(self, username, password) -> bool:
        try:
            login_button = ""
            try:
                login_button = self.driver.find_element(By.CSS_SELECTOR,self.login_btn_selector)
            except NoSuchElementException:
                return True
            
            print("Login requested")

            login_button.click()

            rental_username = self.driver.find_element(By.CSS_SELECTOR,"div.setting-inner:nth-child(3) > form:nth-child(1) > p:nth-child(4) > input:nth-child(1)")
            if username == None:
                username = input("Enter username: ")
            rental_username.send_keys(username)

            if password == None:
                password = maskpass.askpass(prompt="Enter password: ",mask="*")
            rental_password = self.driver.find_element(By.CSS_SELECTOR,"div.setting-inner:nth-child(3) > form:nth-child(1) > p:nth-child(5) > input:nth-child(1)")
            rental_password.send_keys(password)

            login_enter_button = self.driver.find_element(By.CSS_SELECTOR,"div.setting-inner:nth-child(3) > form:nth-child(1) > div:nth-child(7) > button:nth-child(1)")

            print("Entering credentials...")
            login_enter_button.click()
            # if login successful, the page should reload with the pages.
            return True
        except:
            print("Login failed.")
            return False

    def get_pages(self):

        try:
            all_pages = self.driver.find_elements(By.CSS_SELECTOR,self.img_selector)
            print(f"-> {len(all_pages)} Images detected (including ad pages, dummy pages, etc).")
            print("Beginning scrape...") 
            # get images, loop runs until elem without canvas is reached
            for i, page in enumerate(all_pages):
                all_pages = self.driver.find_elements(By.CSS_SELECTOR,self.img_selector) # needs to be updated each time

                # Skip the first dummy page
                try:
                    # NOTE: this try-except block guarantees that the scraper flips 1 page ahead of the images it is actually saving. Might be a good idea to look into better ways to circumvent this dummy page.
                    page.find_element(By.CLASS_NAME,"page-dummy")
                    continue 
                except NoSuchElementException:

                    # Get canvas images. End of chapter is non-canvas imgs, end scrape once those are reached
                    try:
                        canvas_element = page.find_element(By.TAG_NAME,"canvas")
                    except NoSuchElementException:
                        print("End of chapter found, moving to save step")
                        break

                    canvas_base64 = self.driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);",canvas_element)
                    print(f"Got {i + 1} image{"" if i == 0 else "s"}...",end="\r")
                    canvas_png = base64.b64decode(canvas_base64)
                    self.images.append(canvas_png)

                    # click forward a page
                    if i % 2 == 0:
                        next_page = self.driver.find_element(By.CSS_SELECTOR,self.page_turn_selector)
                        next_page.click()
                        time.sleep(0.5)
        except Exception as e:
            print(f"\nAn error was caught during scraping:\n{e}\nAborting")

    def save_pages(self):
        if len(self.images) > 0:
            os.makedirs(os.path.dirname(f"{self.dir}/"), exist_ok=True)
            for id, img in enumerate(self.images):
                print(f"Saving {id + 1}.png...")
                with open(f"{self.dir}/{id + 1}.png","wb") as f:
                    f.write(img)
            print(f"\nImages saved to local directory '{os.getcwd()}/{self.dir}/'.")