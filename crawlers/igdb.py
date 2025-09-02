import json
import requests
from crawlers.crawler import Crawler
from datetime import datetime
from util.utility import get_best_match
from util.config import IGDB_TOKEN, IGDB_CLIENT_SECRET, IGDB_CLIENT_ID

class IGDBCrawler(Crawler):

    def __init__(self):
        super().__init__()
        self.igdb_token = IGDB_TOKEN
        self.igdb_client_id = IGDB_CLIENT_ID
        self.igdb_client_secret = IGDB_CLIENT_SECRET
        self.headers = {'Client-ID': self.igdb_client_id, 'Authorization': 'Bearer ' + self.igdb_token}
        self.igdb_categories = {0: 'Main Game', 1: 'DLC', 2: 'Expansion', 3: 'Bundle', 4: 'Standalone Expansion',
                                5: 'Mod', 6: 'Episode', 7: 'Season', 8: 'Remake', 9: 'Remaster', 10: 'Expanded Game',
                                11: 'Port', 12: 'Fork', 13: 'Pack', 14: 'Update'}

    def get_url(self, title, year=None):
        query = None
        success = False
        best_search_name = ''
        best_search_id = ''
        best_score = 0

        if query is None:
            query = '"; fields name, first_release_date; where platforms.category!=(3); limit 30;'

        try:
            search_query = 'search "' + title + query
            response = requests.post('https://api.igdb.com/v4/games', headers=self.headers, data=search_query)
            search_results = json.loads(response.content.decode('utf-8'))
            candidates = [v['name'] for v in search_results]
            candidate_years = [int(datetime.fromtimestamp(v['first_release_date']).strftime('%Y')) 
                               if 'first_release_date' in v else 0 for v in search_results]
            best_match = get_best_match(candidates=candidates, title=title, title_year=year, candidates_years=candidate_years)
            best_search_name = search_results[best_match[0]]['name']
            best_search_id = search_results[best_match[0]]['id']
            best_score = best_match[1]
            if best_score >= self.accepted_score:
                success = True
        except Exception as _:
            pass
        return {'igdb-title': best_search_name, 'igdb-url': best_search_id, 
                'igdb-score': best_score, 'igdb-success': success}
    

    def get_info(self, url, score):
        game_id = url
        igdb_dict = {'igdb-id': game_id, 'igdb-success': False}
        if score > self.accepted_score:
            try:
                query = 'fields name,alternative_names.name,game_engines.name,artworks.url,similar_games.name, remakes.name, remasters.name,'\
                        'cover.url,dlcs.name,expansions.name,first_release_date,player_perspectives.name,screenshots.url,standalone_expansions.name,'\
                        'franchise.name,themes.name,keywords.name,screenshots.url,category,rating,genres.name,summary,storyline;'
                
                response = requests.post('https://api.igdb.com/v4/games', headers=self.headers, data=query + ' where id=' + str(game_id) + ';')
                game = json.loads(response.content.decode('utf-8'))[0]

                igdb_dict['igdb-name'] = game['name']
                single_keys = ['rating', 'storyline', 'summary']
                list_keys = ['alternative_names', 'dlcs', 'standalone_expansions', 'game_engines', 'genres','keywords', 
                            'player_perspectives', 'remakes', 'remasters', 'similar_games', 'standalone_expansion', 'themes']
                image_keys = ['artworks', 'screenshots']

                for key in single_keys:
                    if key in game:
                        igdb_dict['igdb-'+key] = game[key]
                for key in list_keys:
                    if key in game:
                        igdb_dict['igdb-'+key] =  '; '.join([v['name'] for v in game[key]])
                for key in image_keys:
                    if key in game:
                        igdb_dict['igdb-'+key] =  [('https:' + v['url']).replace('t_thumb', 't_1080p') for v in game[key]]
                if 'category' in game:
                    igdb_dict['igdb-category'] = self.igdb_categories[game['category']]
                if 'cover' in game:
                    igdb_dict['igdb-cover'] = 'https:' + game['cover']['url'].replace('t_thumb', 't_1080p')
                if 'first_release_date' in game:
                    igdb_dict['igdb-release-date'] =  datetime.fromtimestamp(game['first_release_date']).strftime('%d %b, %Y')
                igdb_dict['igdb-success'] = True
            except Exception as _:
                pass
        return igdb_dict

    def get_api_info(self, title):
        return super().get_api_info(title)
    
    def get_raw_info(self, url):
        return super().get_raw_info(url)
