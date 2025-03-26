from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
# undetected module adds some standard anti-bot detection protocols 
import time, base64, undetected_chromedriver as uc, maskpass

# local imports
from objs.scrape_config import ScrapeConfig


# Scraper module intended to scrape raws from youngchampion.
# Example link: https://youngchampion.jp/episodes/32d1bb62782b8/


# current chapter to get: 19 https://youngchampion.jp/episodes/992fa25877712/

# canvas_selector = "-cv-page-canvas" -> 1st child is the canvas element
# navigation_selector = ".-cv-nav mode-l"
# page_container = ".cv-page"

# last page selector: "#xCVLastPage"

scrape_config = ScrapeConfig("champion-nanoscrape","-cv-page-canvas")
scrape_config.from_args() # get command line arguments

scrape_config.login_username = "FortiethAtom4"
scrape_config.login_password = "MushroomsOP16!"

# helper function to log into the site to scrape paid chapters.
def do_login():
    login_button = None
    try:
        login_button = driver.find_element(By.CLASS_NAME,"login-popup-login-btn")
    except NoSuchElementException:
        return True
    
    print("Login requested")
    try:
        login_button.click()
        time.sleep(3) # do more later but for now whatever


        # how nice of them to use unique IDs to make this much easier
        rental_username = driver.find_element(By.CSS_SELECTOR,"input.form-control:nth-child(2)")
        if scrape_config.login_username == "":
            scrape_config.login_username = input("Enter username: ")
        rental_username.send_keys(scrape_config.login_username)

        if scrape_config.login_password == "":
            scrape_config.login_password = maskpass.askpass(prompt="Enter password: ",mask="*")
        rental_password = driver.find_element(By.CSS_SELECTOR,"#password")
        rental_password.send_keys(scrape_config.login_password)

        login_enter_button = driver.find_element(By.CSS_SELECTOR,"#btn-login")

        print("Entering credentials...")
        login_enter_button.click()
        return True
    except:
        return False
    # if login successful, the page should reload with the pages.


options = uc.ChromeOptions()
options.add_argument("--disable-web-security")
options.add_argument("--headless")
# add options here, preferably from scrape_config
driver = uc.Chrome(options=options)
images: list = []

print(f"Opening {scrape_config.url}...")
driver.get(scrape_config.url)
# driver.maximize_window()

resp = do_login()
if resp:
    print("-> Login successful.")

# wait until page content is actually loaded
pages_present = expected_conditions.element_to_be_clickable((By.CLASS_NAME,"-cv-inst-btn")) # TODO catch wait errors for bad links
timeout = 10 # seconds to wait until timeout
WebDriverWait(driver, timeout).until(pages_present)

help_window_close_button = driver.find_element(By.CLASS_NAME,"-cv-inst-btn")
help_window_close_button.click()

time.sleep(5) # had to add 5 seconds after pages present to catch everything. Jank but highly functional for now

#count number of pages
all_pages = driver.find_elements(By.CLASS_NAME,scrape_config.image_selector)

print(f"-> {len(all_pages)} images detected.")

print("Beginning scrape...")
scrape_config.make_directory() 
try:
# get images, loop runs until elem without canvas is reached
    for i, page in enumerate(all_pages):
        all_pages = driver.find_elements(By.CLASS_NAME,scrape_config.image_selector) # needs to be updated each time
        canvas_element = ""
        # end of chapter has pages without canvas, use those to break loop
        try:
            canvas_element = page.find_element(By.TAG_NAME,"canvas")
        except NoSuchElementException:
                # print("\nEnd of chapter found, breaking loop")
                continue
        canvas_base64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);",canvas_element)
        print(f"Got {i + 1} image{"" if i == 0 else "s"}...",end="\r")
        canvas_png = base64.b64decode(canvas_base64)
        images.append(canvas_png)

        # click forward a page
        if i % 2 == 0:
            next_page = driver.find_element(By.CLASS_NAME,"mode-l")
            next_page.click()
            time.sleep(0.5)
    
except Exception as e:
    print(f"\nAn error was caught during scraping:\n{e}\nAborting")
finally:
    # driver.close()
    if len(images) > 0:
        for id, img in enumerate(images):
            print(f"Saving {id + 1}.png...")
            with open(f"{scrape_config.directory}/page_{id + 1}.png","wb") as f:
                f.write(img)
        print(f"\nImages saved to local directory '{scrape_config.directory}/'.")

    print("\n--Scrape complete--\n")