import argparse, os

class ScrapeConfig():
    def __init__(self, program_name: str, image_selector: str):
        self.program_name: str = program_name
        self.url: str = ""
        self.directory: str = "images"
        self.image_selector: str = image_selector
    
    def from_args(self):
        parser = argparse.ArgumentParser(self.program_name)
        parser.add_argument("url", help="URL to scrape from")
        parser.add_argument("-d", "--directory", help="string to a custom directory to save the scraped images. Defaults to 'images'.")
        # add more args for selenium options
        args = parser.parse_args()

        self.url = args.url
        if args.directory is not None:
            self.directory = args.directory

    def make_directory(self):
        os.makedirs(os.path.dirname(f"{self.directory}/"), exist_ok=True)


