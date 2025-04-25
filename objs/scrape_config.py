import argparse, os


class ScrapeConfig():

    def __init__(self, program_name: str, image_selector: str):
        self.program_name: str = program_name
        self.url: str = ""
        self.directory: str = "images"
        self.image_selector: str = image_selector
        self.parser = argparse.ArgumentParser(self.program_name)
        self.args = "" # args parsed from command line

        # login info, not always necessary depending on the site
        self.login_username = ""
        self.login_password = ""

        self.login_button_selector = ""

    def add_arg(self,option: str, option_long: str = None, help: str = ""):
        self.parser.add_argument(option,option_long,help=help)
 
    # TODO remove
    def from_args(self):
        self.parser.add_argument("url", help="URL to scrape from")
        self.parser.add_argument("-d", "--directory", help="relative path to a custom directory to save the scraped images. Defaults to 'images'.")
        self.args = self.parser.parse_args()
        self.url = self.args.url
        if self.args.directory is not None:
            self.directory = self.args.directory
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("~~~~~~~~~~NANOSCRAPE~~~~~~~~~~")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("nanoscrape-python version 3/2025.")
        print(f"Starting script '{self.program_name}'...")
        # add more args for selenium options
        

    def make_directory(self):
        os.makedirs(os.path.dirname(f"{self.directory}/"), exist_ok=True)


