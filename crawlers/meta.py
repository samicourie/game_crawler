import re
from crawlers.crawler import Crawler
from util.utility import get_soup, get_best_match

class MetaCrawler(Crawler):

    def __init__(self):
        super().__init__()
        self.base_meta = 'https://www.metacritic.com'

    def get_url(self, title, year=None):
        temp_title = title
        # score, edist_score = 0, 0
        # url, edist_url = '', ''
        score = 0
        url = ''
        success = False

        try:
            base_url = 'https://www.metacritic.com/search/'
            new_title = title
            url = base_url + new_title + '/?page=1&category=13'

            soup = get_soup(url)
            search_results = soup.find_all('a', {'class': 'c-pageSiteSearch-results-item'})[:15]
            candidates = []
            candidate_years = []
            urls = []
            for result in search_results:
                p_elem = result.find('p')
                search_title = p_elem.text.strip()
                search_title = re.sub(' +', ' ', search_title)
                search_title = search_title.replace('\n', '')
                if 'ios' in result.attrs['href']:
                    continue
                urls.append(self.base_meta + result.attrs['href'])
                candidates.append(search_title)

                try:
                    game_year = result.find('span', {'class': 'u-text-uppercase'}).text.split(', ')[1].replace('\n', '')
                    candidate_years.append(int(game_year))
                except Exception as _:
                    candidate_years.append(0)

            best_candidate = get_best_match(candidates, title, title_year=year, candidates_years=candidate_years)
            temp_title = candidates[best_candidate[0]]
            score = best_candidate[1]
            url = urls[best_candidate[0]]
            if score >= self.accepted_score:
                success = True
        except Exception as _:
            pass

        return {'metacritics-title': temp_title,
                'metacritics-score': score, # 'metacritics-edist-score': edist_score,
                'metacritics-url': url, # 'metacritics-edist-url': edist_url, 
                'metacritics-success': success}


    def get_info(self, url, score):
        meta_score = float(score)
        meta_description = '#'
        critics = ''
        users = ''
        date = ''
        success = False

        if meta_score >= self.accepted_score:
            try:
                critics = ''
                users = ''
                soup = get_soup(url)
                meta_description = soup.find('meta', {'name': 'description'}).attrs['content']
                score_div = soup.find('div', {'class': 'c-reviewsSection'})
                try:
                    critics = score_div.find('div', {'class': 'c-siteReviewScore_background-critic_large'}).find('span').text
                except Exception as e:
                    critics = ''
                try:
                    users = score_div.find('div', {'class': 'c-siteReviewScore_background-user'}).find('span').text
                except Exception as e:
                    users = ''

                try:
                    date = soup.find('div', {'class': 'c-gameDetails_ReleaseDate'}).find('span', {'class': 'g-color-gray70'}).text
                except Exception as _:
                    date = ''
                success = True
            except Exception as _:
                pass
        
        return {'metacritics-description': meta_description, 'metacritics-success': success,
                'metacritics-critics': critics, 'metacritics-users': users, 'metacritics-release-date': date}

    def get_api_info(self, title):
        return super().get_api_info(title)

    def get_raw_info(self, url):
        return super().get_raw_info(url)
