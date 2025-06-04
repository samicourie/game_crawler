import re
from crawlers.crawler import Crawler
from util.utility import get_soup, get_best_match


class BackloggdCrawler(Crawler):

    def __init__(self):
        super().__init__()
        self.base_backloggd = 'https://backloggd.com'

    def get_url(self, title):
        score = 0
        url = ''
        success = False
        try:
            new_title = title.replace('-', ' ').strip()
            new_title = re.sub(' +', ' ', new_title)
            url = self.base_backloggd + '/search/games/' + new_title + '/'
            soup = get_soup(url)
            candidates_elems = soup.find('div', {'id': 'search-results'}).find_all('a')
            candidates_a = []
            for elem in candidates_elems:
                img_elem = elem.find('img')
                if img_elem is not None and 'alt' in img_elem.attrs:
                    candidates_a.append(elem) 
            candidates_urls = [v.attrs['href'] for v in candidates_a]
            candidates_titles = [v.find('img').attrs['alt'] for v in candidates_a]
            best_candidate = get_best_match(candidates_titles, title)
            backloggd_title = candidates_titles[best_candidate[0]]
            score = best_candidate[1]
            url = self.base_backloggd + candidates_urls[best_candidate[0]]
            success = True
        except Exception as _:
            pass

        return {'backloggd-title': backloggd_title,
                'backloggd-score': score,
                'backloggd-url': url, 'backloggd-success': success}
    

    def get_info(self, url, score):
        backloggd_score = float(score)
        backloggd_description = '#'
        backloggd_rating = ''
        split_ratings = ''
        success = False

        if backloggd_score >= self.accepted_score:
            try:
                soup = get_soup(url)
                backloggd_description = soup.find('div', {'id': 'collapseSummary'}).text
                backloggd_rating = soup.find('div', {'id': 'game-rating'}).find('h1').text
                side_content = soup.find('div', {'class': 'side-section'}).find_all('div', {'class': 'col px-0 top-tooltip'})
                ratings = [v.attrs['data-tippy-content'] for v in side_content]
                count_ratings = [v.split(' ★ ')[0] for v in ratings]
                split_ratings = {v.split(' | ')[1]: v.split(' | ')[0] for v in count_ratings}
                success = True
            except Exception as _:
                pass
        
        return {'backloggd-description': backloggd_description, 'backloggd-success': success, 
                'backloggd-rating': backloggd_rating, 'backloggd-split-rating': split_ratings}
    
    def get_api_info(self, title):
        return super().get_api_info(title)
