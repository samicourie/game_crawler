
from abc import ABC, abstractmethod

class Crawler(ABC):

    def __init__(self, accepted_score=0.75):
        super().__init__()
        self._accepted_score = accepted_score

    @property
    def accepted_score(self):
        return self._accepted_score
    
    @accepted_score.setter
    def accepted_score(self, value):
        self._accepted_score = value
    
    @abstractmethod
    def get_url(self, title, year=None):
        pass

    @abstractmethod
    def get_info(self, url, score):
        pass

    @abstractmethod
    def get_api_info(self, title, year=None):
        pass
    
    @abstractmethod
    def get_raw_info(self, url, year=None):
        pass
