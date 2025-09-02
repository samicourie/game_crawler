import json
import time
from crawlers.crawler import Crawler
from util.utility import get_best_match
from util.config import RAWG_KEY
from util.utility import get_soup, get_best_match

class RawgCrawler(Crawler):

    def __init__(self):
        super().__init__()
        self.url_base = 'https://rawg.io/games/'
        self.base_rawg = 'https://rawg.io/api/games?page_size=15&search='
        self.base_rawg_2 = '&page=1&key=' + RAWG_KEY
        self.suggestion_page = 'https://rawg.io/api/games/title/suggested?page=1&page_size=15&key=c542e67aec3a4340908f9de9e86038af'
        self.achievements_page = 'https://rawg.io/api/games/title/achievements?page=1&page_size=XXXXX&key=c542e67aec3a4340908f9de9e86038af'
    
    def get_api_info(self, title, year=None):
        
        try:
            search_url = self.base_rawg + title + self.base_rawg_2
            soup = get_soup(search_url)
            time.sleep(2)
            candidates_elems = json.loads(soup.text)['results']
            candidates_titles = [v['name'] for v in candidates_elems]
            candidates_years = [v['released'] if v['released'] is not None else '0' for v in candidates_elems ]
            candidates_years = [int(v.split('-')[0]) for v in candidates_years]
            candidats_urls = [self.url_base + v['slug'] for v in candidates_elems]
            best_candidate = get_best_match(candidates_titles, title, title_year=year, candidates_years=candidates_years)

            temp_title = candidates_titles[best_candidate[0]]
            score = best_candidate[1]
            url = candidats_urls[best_candidate[0]]
            best_candidate = candidates_elems[best_candidate[0]]

            if score >= self.accepted_score:
                game_obj = {'rawg-title': temp_title}
                game_obj['rawg-release-date'] = best_candidate['released']
                if 'background_image' in best_candidate and best_candidate['background_image']:
                    game_obj['rawg-background-image'] = best_candidate['background_image']
                if 'rating' in best_candidate and best_candidate:
                    game_obj['rawg-score'] = best_candidate['rating']
                if 'ratings' in best_candidate and len(best_candidate['ratings']) > 0:
                    game_obj['rawg-rating'] = {v['title']: v['count'] for v in best_candidate['ratings']}
                if 'short_screenshots' in best_candidate and len(best_candidate['short_screenshots']) > 0:
                    game_obj['rawg-screenshots'] = [v['image'] for v in best_candidate['short_screenshots']]
                if 'genres' in best_candidate and len(best_candidate['genres']) > 0:
                    game_obj['rawg-genres'] = [v['name'] for v in best_candidate['genres']]
                
                soup = get_soup(url)
                time.sleep(1)
                game_obj['rawg-url'] = url
                game_obj['rawg-description'] = soup.find('div', {'class': 'game__about-text'}).text
                raw_page = soup.find('main', {'class': 'page__content'})
                game_obj['rawg-raw'] = str(raw_page)

                try:
                    achievements_elem = soup.find('div', {'class': 'game__achievements'})
                    if achievements_elem:
                        ach_counts = int(achievements_elem.find('a', {'class': 'section-heading__count'}).text.strip().split(' ')[0])
                        soup = get_soup(self.achievements_page.replace('XXXXX', str(ach_counts)).replace('title', best_candidate['slug']))
                        time.sleep(1)
                        achievements = json.loads(soup.text)['results']
                        game_obj['rawg-achievements'] = achievements
                except Exception as _:
                    pass

                try:
                    soup = get_soup(self.suggestion_page.replace('title', best_candidate['slug']))
                    time.sleep(1)
                    suggestions = json.loads(soup.text)['results']
                    game_obj['rawg-similar-games'] = [v['name'] for v in suggestions if v['name'] != temp_title]
                except Exception as _:
                    pass
                game_obj['rawg-success'] = True
                return game_obj

        except Exception as _:
            pass
        return {'rawg-success': False}
    
    def get_url(self, title, year=0):
        return super().get_url(title, year=year)
    
    def get_info(self, url, score):
        return super().get_info(url, score)

    def get_raw_info(self, url):
        return super().get_raw_info(url)
