from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
# undetected module adds some standard anti-bot detection protocols 
import time, undetected_chromedriver as uc, os

# need this stuff to get image and convert into something usable
from binascii import a2b_base64
from PIL import Image
from io import BytesIO 

# need to do something funky to move between pages
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# local imports
from objs.scraper import Scraper


# Scraper module intended to scrape raws of Hoshi Tonde from Booklive.
# https://booklive.jp/product/index/title_id/557255/vol_no/001

# https://booklive.jp/bviewer/s/?cid=557255_001

# honestly kinda crazy that link works. Is the user's ID in the URL??

class ScraperImpl(Scraper):
    
    def __init__(self, url):
        self.url = url
        # webdriver
        self.options = uc.ChromeOptions()
        self.options.enable_downloads = True
        self.options.add_argument("--disable-web-security")
        self.options.add_argument("--headless")
        self.driver = uc.Chrome(options=self.options)

        self.dir = ""
        self.img_selector = "content" #this div contains all pages, but each page has its own ID "content-p[i] where i is page #"
        self.page_turn_selector = "overswipe-wrap"

        self.selector_to_wait_for = ".pages"

        # logins havent been necessary so far
        self.login_btn_selector = "" 
        self.username_field_selector = ""
        self.password_field_selector = ""
        self.enter_login_info_selector = ""

        self.images: list = []

    # logins likely won't be necessary
    def login(self, username, password):
        return True

    def get_pages(self):
        print("-> Images detected.")

        print("Beginning scrape...")
        
        try:
            
            # click on the edge of the page to close the tutorial popup
            actions = ActionChains(self.driver)
            actions.move_to_element_with_offset(self.driver.find_element(By.ID,self.page_turn_selector),-500,0).click().perform()
            
            i = 0
            # page loop
            while self.driver.current_url == self.url:
                page_container_string = f"content-p{i+1}" #page at this location is still divided into 3 parts, will need to stream together with cv2

                page_container = self.driver.find_element(By.ID,page_container_string).find_element(By.CLASS_NAME,"pt-img")
                page_data_parts = []
                page_parts = page_container.find_elements(By.XPATH,"*") #the 3 parts
                for part in page_parts:
                    part_img_child = part.find_element(By.CSS_SELECTOR,"img")

                    # https://stackoverflow.com/questions/64172105/acess-data-image-url-when-the-data-url-is-only-obtain-upon-rendering

                    # 1443x688
                    # my OG 1133x536

                    #TODO issues with image splitting stemming from around here
                    img_base64 = self.driver.execute_script(
    """
    const img = arguments[0];

    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = 1443;
    canvas.height = 688;
    ctx.drawImage(img, 0, 0);

    data_url = canvas.toDataURL('image/png');
    return data_url
    """, 
    part_img_child)
                    binary_data = a2b_base64(img_base64.split(',')[1])
                    
                    final_image_part = Image.open(BytesIO(binary_data))

                    page_data_parts.append(final_image_part)

                #combine 3 parts together
                width = max([image.width for image in page_data_parts])
                height = sum([image.height for image in page_data_parts])
                final_image = Image.new("RGB", (width, height))
                y = 0
                for part in page_data_parts:
                    final_image.paste(part,(0,y+1))
                    y += part.height

                self.images.append(final_image)
                
                print(f"Got {i + 1} image{"" if i == 0 else "s"}...",end="\r")


                # turn a page to load more images
                if i % 2 == 0:
                    actions.send_keys(Keys.LEFT).perform()
                time.sleep(0.2)
                i += 1
                
            print("")
            self.driver.quit()
            
        except Exception as e:
            print(f"\nAn error was caught during scraping:\n{e}\nAborting")

    # images are saved slightly differently, will need to override
    def save_pages(self):
        if len(self.images) > 0:
            os.makedirs(os.path.dirname(f"{self.dir}/"), exist_ok=True)
            for id, img in enumerate(self.images):
                img.save(f'{self.dir}/image_{id+1}.png')
                print(f"Saving image_{id + 1}.png...",end="\r")
        print(f"\nImages saved to local directory '{self.dir}/'.")