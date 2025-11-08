from selenium.webdriver.common.by import By
from PIL import Image
# undetected module adds some standard anti-bot detection protocols, kind of annoying though might remove
import time, io, os, base64, undetected_chromedriver as uc

# local imports
from objs.scraper import Scraper


# Scraper module intended to scrape raws from Takeshobo.
# Example link: https://storia.takeshobo.co.jp/_files/hanegurashi/01/

# canvas_selector = ".c-viewer__comic"
# navigation_selector = ".c-viewer__pager-next"
# page_container = ".c-viewer__pages"

# .p-episode-purchase__btn

# chromedriver fix: https://stackoverflow.com/questions/74817978/oserror-winerror-6-with-undetected-chromedriver

class ScraperImpl(Scraper):
    
    def __init__(self, url):
        self.url = url
        # webdriver
        self.options = uc.ChromeOptions()
        self.options.add_argument("--disable-web-security")
        self.options.add_argument("--headless")
        self.driver = uc.Chrome(options=self.options)

        self.dir = ""
        self.img_selector = "#content"
        self.page_turn_selector = "#menu_transparent"

        self.selector_to_wait_for = "#content"

        self.login_btn_selector = ".p-episode-purchase__btn" 
        self.username_field_selector = "#email"
        self.password_field_selector = "#password"
        self.enter_login_info_selector = "button.btn"

        self.images: list = []

    # logins not yet required, skipping for now
    def login(self, username, password):
        print("Skipped login phase.")
        return True

    def get_pages(self):
        all_pages = self.driver.find_elements(By.CSS_SELECTOR,self.img_selector)
        print("-> Images detected.")

        print("Beginning scrape...")
        try:
        # get images, loop runs until elem without canvas is reached
            for i, page in enumerate(all_pages):
                all_pages = self.driver.find_elements(By.CSS_SELECTOR,self.img_selector) # needs to be updated each time

                # navigate to child
                page_child_elem = page.find_element(By.CSS_SELECTOR,f"#content-p{i}")

                # list of img html elements
                page_part_elems = page_child_elem.find_elements(By.TAG_NAME,"img")

                # turn into list of src strings
                for i, elem in enumerate(page_part_elems):
                    src = elem.get_attribute('src')

                    # this works???
                    js_script = """
var img = arguments[0];
var blobUrl = img.src;
return fetch(blobUrl)
    .then(response => response.blob())
    .then(blob => {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(blob);
            });
        });
    """
                    base64_image_piece = self.driver.execute_script(js_script, elem)
                    base64_image_piece = base64_image_piece.split(",")[1]

                    # this is bytes for one piece of image page, can save very easily with file.write()
                    piece_bytes = bytearray(base64.b64decode(base64_image_piece))

                    piece = Image.open(io.BytesIO(piece_bytes))
                    page_part_elems[i] = piece

                # stitch the pieces together - SLIGHTLY OFF, THERE IS OVERLAP IN THE IMAGES #TODO
                img_width = min(i.width for i in page_part_elems)
                img_height = sum(i.height for i in page_part_elems)
                
                final_img = Image.new("RGB",size=(img_width,img_height))
                
                for i, elem in enumerate(page_part_elems):
                    height_img_paste = int(i * img_height/3)
                    final_img.paste(elem,(0,height_img_paste))
                
                self.images.append(final_img)
               
                # canvas_base64 = self.driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);",canvas_element)
                print(f"Got {i + 1} image{"" if i == 0 else "s"}...",end="\r")
                

                # click forward a page once stitch is done
                if i % 2 == 0:
                    next_page = self.driver.find_element(By.CLASS_NAME,self.page_turn_selector)
                    next_page.click()
                    time.sleep(1)

            self.driver.quit()
            
        except Exception as e:
            print(f"\nAn error was caught during scraping:\n{e}\nAborting")

    def save_pages(self):
        if len(self.images) > 0:
            os.makedirs(os.path.dirname(f"{self.dir}/"), exist_ok=True)
            for id, img in enumerate(self.images):
                print(f"Saving {id + 1}.png...",end="\r")
                img.save(f"{self.dir}/page_{id + 1}.png")
            print(f"\nImages saved to local directory '{self.dir}/'.")
        else:
            print("\nWarning: no images to save.")
