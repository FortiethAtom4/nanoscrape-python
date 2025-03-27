from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import requests

# local imports
from objs.scrape_config import ScrapeConfig


# Scraper module intended to scrape raws of Kowloon Generic Romance from WeLoMa. 
# Example link: https://weloma.art/472/150451/


scrape_config = ScrapeConfig("weloma-nanoscrape", "chapter-img")
scrape_config.from_args() # get command line arguments

options = Options()
options.add_argument("--headless")
# add options here, preferably from scrape_config
try:
    imgs: list[str] = []
    driver = webdriver.Firefox(options=options)
    driver.get(scrape_config.url)

    # get images
    elems = driver.find_elements(By.CLASS_NAME, scrape_config.image_selector)
    for item in elems: 
        imgs.append(item.get_attribute("src"))

    # close page
    driver.quit()

    if len(imgs) == 0:
        raise Exception(f"No images with the correct class name were found at {scrape_config.url}")
    print(f"Number of images found: {len(imgs)}")

    # save images
    scrape_config.make_directory()
    for id, img_url in enumerate(imgs):
        print(f"Saving {img_url}...")
        img_data = requests.get(img_url).content
        with open(f"{scrape_config.directory}/{id + 1}.png","wb") as img:
            img.write(img_data)

    print(f"All images saved at '{scrape_config.directory}/'.")
except Exception as e:
    print(f"\nAn error was caught during scraping:\n{e}\nAborting")
finally:
    print("--Script complete--")