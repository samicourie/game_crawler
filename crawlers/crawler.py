
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
    
    def crawl(self, title, year=0):

        if self.site in ['hltb', 'giantbomb', 'rawg']:
            site_info = self.get_api_info(title, year)
        else:
            url_info = self.get_url(title, year)
            site_info = dict()
            if url_info[self.site+'-success'] and url_info[self.site+'-score'] >= self.accepted_score:
                site_info = self.get_info(url_info[self.site+'-url'], url_info[self.site+'-score'])
                site_info.update(url_info)

        if site_info.get(self.site + '-success', False):
            return site_info

        return {self.site + '-success': False}

    @abstractmethod
    def get_url(self, title, year=0):
        pass

    @abstractmethod
    def get_info(self, url, score):
        pass

    @abstractmethod
    def get_api_info(self, title, year=0):
        pass
    
    @abstractmethod
    def get_raw_info(self, url, year=0):
        pass
