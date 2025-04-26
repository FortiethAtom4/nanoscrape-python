from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
# undetected module adds some standard anti-bot detection protocols 
import time, base64, maskpass, undetected_chromedriver as uc

# local imports
from objs.scrape_config import ScrapeConfig

# Scraper module intended to scrape raws of Kowloon Generic Romance from ShonenJumpPlus.
# Example link: https://shonenjumpplus.com/episode/17106567256754793848
# This site often requires a login and payment to scrape, so remote login will be required in order to scrape.

# pages are held in canvases with class "page-image" within <p> tags with class "page-area"

# fix for undetected-chromedriver OS error: https://stackoverflow.com/questions/74817978/oserror-winerror-6-with-undetected-chromedriver/76497142

# TODO: use wait functionality to replace janky hard-coded wait times

# image is a child Canvas element of the selected for here
scrape_config = ScrapeConfig("shonenjumpplus-nanoscrape","page-area")
scrape_config.add_arg("-u","--username","Username for login")
scrape_config.add_arg("-p","--password","Password for login")
scrape_config.from_args()

scrape_config.login_username = scrape_config.args.username
scrape_config.login_password = scrape_config.args.password



options = uc.ChromeOptions()
options.add_argument("--disable-web-security")
options.add_argument("--headless")
# add options here, preferably from scrape_config
driver = uc.Chrome(options=options)
images: list = []

print(f"Opening {scrape_config.url}...")
driver.get(scrape_config.url)


# do login

# rental button selector: ".rental-button-box"
# rental username: "div.setting-inner:nth-child(3) > form:nth-child(1) > p:nth-child(4) > input:nth-child(1)"
# rental password: "div.setting-inner:nth-child(3) > form:nth-child(1) > p:nth-child(5) > input:nth-child(1)"

def do_login():
    login_button = ""
    try:
        login_button = driver.find_element(By.CLASS_NAME,"rental-button-box")
    except NoSuchElementException:
        return
    
    print("Login requested")

    login_button.click()

    rental_username = driver.find_element(By.CSS_SELECTOR,"div.setting-inner:nth-child(3) > form:nth-child(1) > p:nth-child(4) > input:nth-child(1)")
    if scrape_config.login_username == None:
        scrape_config.login_username = input("Enter username: ")
    rental_username.send_keys(scrape_config.login_username)

    if scrape_config.login_password == None:
        scrape_config.login_password = maskpass.askpass(prompt="Enter password: ",mask="*")
    rental_password = driver.find_element(By.CSS_SELECTOR,"div.setting-inner:nth-child(3) > form:nth-child(1) > p:nth-child(5) > input:nth-child(1)")
    rental_password.send_keys(scrape_config.login_password)

    login_enter_button = driver.find_element(By.CSS_SELECTOR,"div.setting-inner:nth-child(3) > form:nth-child(1) > div:nth-child(7) > button:nth-child(1)")

    print("Entering credentials...")
    login_enter_button.click()
    # if login successful, the page should reload with the pages.

def sjp_nanoscrape():

    do_login()
    pages_present = expected_conditions.element_to_be_clickable((By.CLASS_NAME,"page-navigation-forward")) # TODO catch wait errors for bad links
    timeout = 10 # seconds to wait until timeout
    WebDriverWait(driver, timeout).until(pages_present)
    # time.sleep(3)
    #count number of pages
    all_pages = driver.find_elements(By.CLASS_NAME,scrape_config.image_selector)
    print(f"-> {len(all_pages)} Images detected (including ad pages, dummy pages, etc).")

    print("Beginning scrape...")
    scrape_config.make_directory() 
    try:
    # get images, loop runs until elem without canvas is reached
        for i, page in enumerate(all_pages):
            all_pages = driver.find_elements(By.CLASS_NAME,scrape_config.image_selector) # needs to be updated each time


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
                    print("End of chapter found, downloading images")
                    break

                canvas_base64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);",canvas_element)
                print(f"Got {i + 1} image{"" if i == 0 else "s"}...",end="\r")
                canvas_png = base64.b64decode(canvas_base64)
                images.append(canvas_png)

                # click forward a page
                if i % 2 == 0:
                    next_page = driver.find_element(By.CLASS_NAME,"page-navigation-forward")
                    next_page.click()
                    time.sleep(1.5)
        
    except Exception as e:
        print(f"\nAn error was caught during scraping:\n{e}\nAborting")
    finally:
        driver.close()
        if len(images) > 0:
            for id, img in enumerate(images):
                print(f"Saving {id + 1}.png...")
                with open(f"{scrape_config.directory}/{id + 1}.png","wb") as f:
                    f.write(img)
            print(f"\nImages saved to local directory '{scrape_config.directory}/'.")

        print("\n--Scrape complete--\n")


sjp_nanoscrape()