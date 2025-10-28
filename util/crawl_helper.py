from crawlers.backloggd import BackloggdCrawler
from crawlers.gamesdb import GamesDBCrawler
from crawlers.giantbomb import GiantbombCrawler
from crawlers.hltb import HLTBCrawler
from crawlers.igdb import IGDBCrawler
from crawlers.meta import MetaCrawler
from crawlers.moby import MobyCrawler
from crawlers.psnprofiles import PSNProfilesCrawler
from crawlers.rawg_2 import RawgCrawler
from crawlers.steam import SteamCrawler
from crawlers.wikipedia import WikipediaCrawler


class CrawlHelper():

    def __init__(self):
        self.crawler_dict = {
            'backloggd': BackloggdCrawler,
            'gamesdb': GamesDBCrawler,
            'giantbomb': GiantbombCrawler,
            'hltb': HLTBCrawler,
            'igdb': IGDBCrawler,
            'metacritics': MetaCrawler,
            'moby': MobyCrawler,
            'psnprofiles': PSNProfilesCrawler,
            'rawg': RawgCrawler,
            'steam': SteamCrawler,
            'wikipedia': WikipediaCrawler
            }
    
    def crawl_urls(self, entries):
        
        results = dict()
        for entry in entries:
            crawler = self.crawler_dict[entry['site']]()
            results[entry['site']] = crawler.get_info(entry['url'], score=1)
        
        return results