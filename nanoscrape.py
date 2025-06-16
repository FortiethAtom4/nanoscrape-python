#Main module that does everything.
from objs.scraper import Scraper
import importlib,  argparse
from urllib.parse import urlparse

class BadLogin(Exception):
    def __init__(self):
        self.msg = "Login unsuccessful."
        super().__init__(self.msg)

def nanoscrape():
    parser = argparse.ArgumentParser("nanoscrape")
    parser.add_argument("url", help="URL to scrape from")
    parser.add_argument("-d", "--directory", help="relative path to a custom directory to save the scraped images. Defaults to 'images'.")
    parser.add_argument("-u","--username",help="Username for login",default=None)
    parser.add_argument("-p","--password",help="Password for login",default=None)
    args = parser.parse_args()

    scraper: Scraper = None

    # match scraper to correct subclass by url domain name
    url = urlparse(args.url)
    scraper_class = "" #to be loaded dynamically
    match url.hostname:
        case "ciao.shogakukan.co.jp":
            scraper_class = "objs.ciao"

        case "youngchampion.jp":
            scraper_class = "objs.champion"

        case "booklive.jp":
            scraper_class = "objs.booklive"

        case "shonenjumpplus.com":
            scraper_class = "objs.shonenjumpplus"

        case _:
            print(f"URL {url.geturl()} not recognized by nanoscrape. Please check and try again.")
            return
        
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("~~~~~~~~~~NANOSCRAPE~~~~~~~~~~")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("nanoscrape-python version 4/2025.")

    # load scraper functions for detected website
    scraper_class = getattr(importlib.import_module(scraper_class),"ScraperImpl")
    scraper = scraper_class(url.geturl())
    # setup scraper.dir
    scraper.dir = "images" if args.directory is None else args.directory
    # do the scrape
    try:
        scraper.load_page()

        # login functions should come with built-in check for login elements
        if not scraper.login(args.username, args.password):
            raise BadLogin()
        
        print("-> Login phase complete.")

        scraper.get_pages()

    except Exception as e:
        print(e)
    finally:
        scraper.save_pages()
        print("\n--Scrape complete--\n")

nanoscrape()