import re
import json
from crawlers.crawler import Crawler
from util.utility import get_soup, get_best_match

class RiotCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.base_riot = 'https://en.riotpixels.com'

    def get_url(self, title):
        temp_title = title
        score = 0
        url = ''
        success = False
        try:
            new_title = title.replace('-', ' ').strip()
            new_title = re.sub(' +', ' ', new_title)
            new_title = new_title.replace(' ', '&')
            url = self.base_riot + '/search/' + new_title + '/'
            soup = get_soup(url, cloud_scrapper=True)
            candidates = json.loads(soup.text)
            candidates_titles = [v['value'] for v in candidates]
            best_candidate = get_best_match(candidates_titles, title)

            temp_title = candidates[best_candidate[0]]['value']
            score = best_candidate[1]
            url = self.base_riot + '/games/' + candidates[best_candidate[0]]['id'].replace('games-', '') + '/screenshots/'
            success = True
            
        except Exception as _:
            pass

        return {'riot-title': temp_title,
                'riot-score': score,
                'riot-url': url, 'riot-success': success}
    
    def get_info(self, url, score):
        riot_score = float(score)
        riot_images = []
        success = False

        if riot_score >= self.accepted_score:
            try:
                soup = get_soup(url, cloud_scrapper=True)
                images_section = soup.find('section', {'class': 'gallery-list-more'})
                images_li_elems = images_section.find_all('li')
                for img_li in images_li_elems:
                    img_sizes = img_li.find('a').attrs['onclick'].replace('return ', '')
                    img_sizes = json.loads(img_sizes)
                    biggest_size = 0
                    biggest_url = ''
                    for size in img_sizes:
                        if size['h'] > biggest_size:
                            biggest_size = size['h']
                            biggest_url = size['u']
                    riot_images.append(biggest_url)
                success = True
            except Exception as _:
                pass
        
        return {'riot-screenshots': riot_images, 'riot-success': success}

    def get_api_info(self, title):
        return super().get_api_info(title)

    def get_raw_info(self, url):
        return super().get_raw_info(url)
