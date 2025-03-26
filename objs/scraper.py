from abc import ABC, abstractmethod

class Scraper(ABC):

    @abstractmethod
    def __init__(self):
        pass

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