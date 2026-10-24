import re
import requests
from urllib.parse import quote
from crawlers.crawler import Crawler
from util.utility import get_soup, get_best_match

class ExophaseCrawler(Crawler):

    def __init__(self):
        super().__init__()
        self.site = 'exophase'
        self.base_exophase = 'https://api.exophase.com/public/archive/games?q=SLUG&sort=updated&userId=0'
        self.platforms_dict = {'3DS': ['3ds'], 'DreamCast': ['retro'], 'GBA': ['retro'], 'GC - WII': ['retro'],
                                'N64': ['retro'], 'NDS': ['retro'], 'NS': ['NS'], 'PC': ['epic', 'steam', 'gog', 'psn'], 
                                'PC / Indie': ['epic', 'steam', 'gog', 'psn'],
                                'PS1': ['retro'], 'PS2': ['retro'], 'PS3': ['psn', 'steam', 'gog'], 
                                'PS4 / PS5': ['psn', 'steam', 'gog'], 'PSP': ['retro'],
                                'SEGA': ['retro'], 'SNES': ['retro'], 'Wii U': ['WII U'], 'Retro': ['retro']}

    def get_url(self, title, year=0):
        temp_title = title
        score = 0
        url = ''
        success = False

        try:
            new_title = title
            slug = quote(re.sub(r'[^a-z0-9ÉéÖ#]+', '-', new_title.lower()).strip('-'), safe="#").replace("#", "%23")
            slug = slug.replace('-', ' ')
            url = self.base_exophase.replace('SLUG', slug)

            response = requests.get(url)
            json_response = response.json()
            game_list = json_response['games']['list'][:20]
            candidates = [[g['title'], g['environment_slug'], g['endpoint_awards'], 
                           g['global_players']] for g in game_list]
            candidates = sorted(candidates, key=lambda v: v[3], reverse=True)
            candidate_years = [0 for _ in candidates]
            ########################################################################################################
            # It is not year, it is platform, just didn't want to change the code a lot.
            accepted_platforms = self.platforms_dict(year)
            ########################################################################################################
            candidates_titles = [v[0] for v in candidates if v[1] in accepted_platforms]
            urls = [v[2] for v in candidates if v[1] in accepted_platforms]
            g_users = [v[3] for v in candidates if v[1] in accepted_platforms]

            best_candidate = get_best_match(candidates_titles, title, title_year=0, candidates_years=candidate_years)
            temp_title = candidates_titles[best_candidate[0]]
            score = best_candidate[1]
            url = urls[best_candidate[0]]
            global_users = g_users[best_candidate[0]]
            if score >= self.accepted_score:
                success = True
        except Exception as _:
            pass

        return {'exophase-title': temp_title, 'exophase-score': score, 'exophase-url': url, 
                'exophase-success': success, 'exophase-global-players': global_users}


    def get_info(self, url, score):
        exophase_score = float(score)
        success = False
        banner_url = ''
        global_players = 0

        if exophase_score >= self.accepted_score:
            try:
                soup = get_soup(url, cloud_scrapper=True)
                try:
                    image_banner = soup.select_one('.image.slide-item')['style']
                    banner_url = image_banner.split('url(')[1].split(')')[0].strip("'\"")
                except Exception as _:
                    pass

                try:
                    main_img = soup.find('a', {'class': 'image'}).find('img').attrs['src']
                    platform = soup.select_one('.info-top-block span').get_text(strip=True)
                except Exception as _:
                    pass
                try:
                    header_ul = soup.find('ul', {'class': 'row justify-content-md-center section-fill overview-top'})
                    header_lis = header_ul.find_all('li')
                    for li in header_lis:
                        li_span = li.find('span').text
                        if li_span == 'Players Tracked':
                            global_players = int(li.find('strong').text.replace(',', ''))
                            break
                except Exception as _:
                    global_players = 0
                    pass

                ul_div = soup.find('div', {'id': 'awards'})
                main_uls = ul_div.find_all('ul')
                main_h3 = ['Base Game'] + [h.text for h in ul_div.find_all('h3')]
                game_trophies = []
                for ind, main_ul in enumerate(main_uls):
                    game_trophies.append({'title': main_h3[ind], 'image': main_img})
                    lis = main_ul.find_all('li')
                    for elem in lis:
                        img = elem.find('img')
                        img_src = img.attrs['src']

                        title = elem.find('div', {'class': 'text-medium award-title hidden-toggle fw-bolder'}).text.strip()
                        description = elem.find('div', {'class': 'award-description hidden-toggle'}).text.strip()

                        count = elem.find('span', {'class': 'tippy'}).text.split(' ')[0]
                        game_trophies.append({'title': title, 'description': description, 
                                              'percentage': count, 'image': img_src})
                if len(main_uls) == 1:
                    game_trophies = game_trophies[1:]
            except Exception as _:
                pass

        success = True
        return {'exophase-success': success, 'exophase-achievements': game_trophies, 
                'exophase-global-players': global_players, 'exophase-image-banner': banner_url, 
                'exophase-platform': platform}

    def get_api_info(self, title):
        return super().get_api_info(title)

    def get_raw_info(self, url):
        return super().get_raw_info(url)
