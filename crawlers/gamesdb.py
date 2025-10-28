import re
import json
from crawlers.crawler import Crawler
from util.utility import get_soup, get_best_match


class GamesDBCrawler(Crawler):

    def __init__(self):
        super().__init__()
        self.site = 'gamesdb'
        self.details_gamesdb = 'https://gamesdb.launchbox-app.com/games/details/'
        self.search_gamesdb = 'https://api.gamesdb.launchbox-app.com/api/search/'
        self.image_base = 'https://images.launchbox-app.com//'
        self.platforms = ['Linux', 'Microsoft Xbox', 'Microsoft Xbox 360', 'Microsoft Xbox One', 'Microsoft Xbox Series X/S',
                          'Nintendo 3DS', 'Nintendo 64', 'Nintendo DS', 'Nintendo Entertainment System', 'Nintendo Game Boy',
                          'Nintendo Game Boy Advance', 'Nintendo Game Boy Color', 'Nintendo GameCube', 'Nintendo Switch',
                          'Nintendo Switch 2', 'Nintendo Wii', 'Nintendo Wii U', 'Sega Genesis', 'Sony Playstation', 
                          'Sony Playstation 2', 'Sony Playstation 3', 'Sony Playstation 4', 'Sony Playstation 5', 'Sony PSP', 
                          'Super Nintendo Entertainment System', 'Windows']

    def get_url(self, title, year=0):
        temp_title = title
        score = 0
        url = ''
        success = False
        try:
            new_title = title.replace(' -', ' ').strip()
            new_title = new_title.replace('- ', ' ').strip()
            new_title = re.sub(' +', ' ', new_title)
            url = self.search_gamesdb + new_title
            soup = get_soup(url)
            json_res = json.loads(soup.text)
            pot_games = json_res['data']
            candidates = []
            keys = []
            for game in pot_games:
                if game['platformName'] in self.platforms:
                # if game['platformName'] == 'Windows':
                    candidates.append(game['name'])
                    keys.append(game['gameKey'])
            best_candidate = get_best_match(candidates, title)
            temp_title = candidates[best_candidate[0]]
            score = best_candidate[1]
            url = self.details_gamesdb + str(keys[best_candidate[0]]) + '-' + temp_title.lower().replace(' ', '-')
            if score >= self.accepted_score:
                success = True
        except Exception as _:
            pass

        return {'gamesdb-title': temp_title,
                'gamesdb-score': score,
                'gamesdb-url': url, 'gamesdb-success': success}
    

    def get_info(self, url, score):
        gamesdb_score = float(score)
        gamesdb_images = dict()
        success = False

        if gamesdb_score >= self.accepted_score:
            try:
                soup = get_soup(url)
                gamescb_description = soup.find('section', {'class': 'game-details-content grid gap-8 md:gap-20'}).find('span', {'class': 'text-body-sm'}).text
                script_text = soup.find('script', {'id': '__NUXT_DATA__'}).text
                script_list = script_text.split(',')
                current_type = 0
                current_image = ''
                for line in script_list:
                    if 'imageTypeName' in line:
                        if current_image != '':
                            gamesdb_images[current_type].append(self.image_base + current_image)
                            current_image = ''
                        current_type = line.split(':')[1]
                        if current_type not in gamesdb_images:
                            gamesdb_images[current_type] = []
                    if '.png' in line or 'jpg' in line:
                        current_image = line.replace('"', '').replace("'", '').strip()
                    if bool(re.fullmatch(r'[a-zA-Z0-9\- \"]+', line)) and re.search(r'[a-zA-Z]', line):
                        if current_type in gamesdb_images and len(gamesdb_images[current_type]) == 0:
                            type_name = line.replace('"', '').strip()
                            gamesdb_images[current_type].append(type_name)
                    
                gamesdb_images[current_type].append(self.image_base + current_image)
                success = True
            except Exception as _:
                pass
        
        return {'gamesdb-description': gamescb_description, 'gamesdb-success': success, 'gamesdb-images': gamesdb_images}
    
    def get_api_info(self, title):
        return super().get_api_info(title)
    
    def get_raw_info(self, url):
        return super().get_raw_info(url)
