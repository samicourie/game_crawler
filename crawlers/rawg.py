import re
import rawg
import asyncio
from crawlers.crawler import Crawler
from util.utility import get_best_match
from util.config import RAWG_KEY


class RawgCrawler(Crawler):

    def __init__(self):
        super().__init__()
        self.rawg_key = RAWG_KEY

    async def get_rawg_requests(self, title, year=0):
        temp_title = title
        score = 0
        description = ''
        success = False
        async with rawg.ApiClient(rawg.Configuration(api_key={'key': self.rawg_key})) as api_client:
            # Create an instance of the API class
            try:
                api = rawg.GamesApi(api_client)
                
                # Making requests
                coros = [api.games_read(id=name) for name in [title]]

                candidates_obj = []

                # Waiting for requests
                for coro in asyncio.as_completed(coros):
                    game: rawg.GameSingle = await coro
                    candidates_obj.append({'id': game.id, 'name': game.name, 
                                           'description': game.description, 
                                           'year': int(game.released.year) if game.released else 0})
                
                candidates = [g['name'] for g in candidates_obj]
                candidates_years = [g['year'] for g in candidates_obj]
                best_candidate = get_best_match(candidates, title, title_year=year, candidates_years=candidates_years)

                temp_title = candidates_obj[best_candidate[0]]['name']
                score = best_candidate[1]
                if score >= self.accepted_score:
                    description = candidates_obj[best_candidate[0]]['description']
                    success = True
                return {'rawg-title': temp_title,
                'rawg-score': score, 'rawg-success': success,
                'rawg-description': description}
            except Exception as _:
                pass
        return {'rawg-success': success}
        
    
    def get_api_info(self, title, year=None):
        rawg_title = re.sub(r'[^a-zA-Z0-9- ]', '', title)
        rawg_title = rawg_title.lower().replace(' ', '-')
        while '--' in rawg_title:
            rawg_title = rawg_title.replace('--', '-')
        rawg_obj = asyncio.get_event_loop().run_until_complete(self.get_rawg_requests(rawg_title, year=year))
        return rawg_obj
    
    def get_url(self, title):
        return super().get_url(title)
    
    def get_info(self, url, score):
        return super().get_info(url, score)
    
    def get_raw_info(self, url):
        return super().get_raw_info(url)
