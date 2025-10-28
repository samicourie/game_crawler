import re
import zlib
from crawlers.crawler import Crawler
from util.utility import get_soup, get_best_match

class SteamCrawler(Crawler):

    def __init__(self):
        super().__init__()
        self.site = 'steam'
        self.base_url = 'https://store.steampowered.com/search/?term='
        self.achiev_url = 'https://steamcommunity.com/stats/{id}/achievements'
        self.charts_url = 'https://steamcharts.com/app/{id}'

    def get_url(self, title, year=0):
        temp_title = title
        # score, edist_score = 0, 0
        score = 0
        # url, edist_url = '', ''
        url = ''
        success = False
        try:
            
            new_title = title.replace(' ', '+')
            url = self.base_url + new_title
            soup = get_soup(url, steam=True)
            urls = []
            search_results = soup.find_all('a', {'class':
                                                    ['search_result_row ds_collapse_flag', 'app_impression_tracked']})[:10]
            candidates = []
            candidates_years = []
            for result in search_results:
                search_title = result.find('span', {'class': 'title'}).text
                urls.append(result.attrs['href'])
                candidates.append(search_title)

                try:
                    release_year = result.find('div', {'class': 'search_released'}).text.split(', ')[1].strip()
                    candidates_years.append(int(release_year) if release_year.isdigit() else 0)
                except Exception as _:
                    candidates_years.append(0)

            best_candidate = get_best_match(candidates, title, title_year=year, candidates_years=candidates_years)
            temp_title = candidates[best_candidate[0]]
            score = best_candidate[1]
            url = urls[best_candidate[0]]
            if score >= self.accepted_score:
                success = True
            # best_edist_candidate = get_best_edit_distance(candidates, title)
            # edist_url = urls[best_edist_candidate[0]]
            # edist_score = best_edist_candidate[1]

        except Exception as _:
            pass

        return {'steam-title': temp_title,
                'steam-score': score, # 'steam-edist-score': edist_score,
                'steam-url': url, # 'steam-edist-url': edist_url,
                'steam-success': success}
    
    def get_info(self, url, score):
        steam_score = float(score)

        steam_description = '#'
        steam_raw = '#'
        steam_summary = '#'
        steam_critics = ''
        steam_atp = ''
        steam_tags = '#'
        steam_nb_users = ''
        steam_genres = '#'
        developers_list = ''
        date = ''
        success = False
        steam_achivements = []
        steam_images = []
        if steam_score >= self.accepted_score:
            try:
                soup = get_soup(url, steam=True)
                steam_description = soup.find('div', {'class': 'game_description_snippet'})
                if steam_description is not None:
                    steam_description = steam_description.text
                    steam_description = steam_description.replace('\r', ' ')
                    steam_description = steam_description.replace('\t', ' ')
                    steam_description = steam_description.replace('\n', ' ')
                    steam_description = steam_description.replace("\'", "'")
                    steam_description = steam_description.strip()
                    steam_description = re.sub(' +', ' ', steam_description)
                else:
                    steam_description = '#'

                steam_summary = soup.find('div', {'id': 'aboutThisGame'})
                if steam_summary is not None:
                    # steam_raw = zlib.compress(str(steam_summary).encode('utf-8'))
                    steam_raw = str(steam_summary)
                    steam_summary = steam_summary.text
                    steam_summary = steam_summary.replace('\r', ' ')
                    steam_summary = steam_summary.replace('\t', ' ')
                    steam_summary = steam_summary.replace('\n', ' ')
                    steam_summary = steam_summary.replace("\'", "'")
                    steam_summary = steam_summary.strip()
                    steam_summary = re.sub(' +', ' ', steam_summary)
                else:
                    steam_summary = '#'

                my_a = soup.find_all('a', {'class': 'user_reviews_summary_row'})
                if len(my_a) > 2:
                    wanted_div = my_a[1]
                else:
                    wanted_div = my_a[0]
                
                try:
                    review_span = soup.find('span', {'class': 'review_summary_count'})
                    if review_span:
                        steam_nb_users = int(review_span.text.replace(',', ''))
                    else:
                        steam_nb_users = int(wanted_div.find('span', {'class': 'responsive_hidden'})
                                                             .text[1:-1].strip()[1:-1].replace(',', ''))
                except Exception as _:
                    pass
                
                try:
                    review_div = soup.find('div', {'class', 'review_language_outliers'})
                    if review_div:
                        steam_critics = review_div.find('span', {'class': 'game_review_summary positive'}).attrs['data-tooltip-html'].split('%')[0]
                    else:
                        steam_critics = wanted_div.attrs['data-tooltip-html'].split('%')[0]
                except Exception as _:
                    pass
        
                try:
                    date = soup.find('div', {'class': 'date'}).text
                except AttributeError as _:
                    date = ''

                steam_genres = [d.text.replace('\t', '').replace('\r', '').replace('\n', '')
                            for d in soup.find_all('a', {'class': 'app_tag'})]
                steam_genres = '; '.join(steam_genres)

                steam_tags = soup.find('div', {'class': ['glance_tags', 'popular_tags']}).find_all('a')
                steam_tags = '; '.join([a.text.replace('\t', '').replace('\n', '') for a in steam_tags])

                screenshot_divs = soup.find_all('div', {'class': 'screenshot_holder'})
                for sc_shot_div in screenshot_divs:
                    image_src = sc_shot_div.find('a').attrs['href']
                    steam_images.append(image_src)
                dev_list_div = soup.find('div', {'id': 'developers_list'})
                
                found_dev_list = []
                dev_list_urls = dev_list_div.find_all('a')
                for link in dev_list_urls:
                    found_dev_list.append(link.text)
                developers_list = '; '.join(found_dev_list)
                success = True

                steam_id = url.split('app/')[1].split('/')[0]
                achiev_url = self.achiev_url.replace('{id}', steam_id)
                soup_achiev = get_soup(achiev_url, steam=True)
                all_achiev = soup_achiev.find_all('div', {'class': 'achieveRow'})
                for achiev in all_achiev:
                    achiev_dict = dict()
                    achiev_dict['image'] = achiev.find('img').attrs['src']
                    achiev_dict['percent'] = achiev.find('div', {'class': 'achievePercent'}).text
                    achiev_dict['name'] = achiev.find('h3').text
                    achiev_dict['description'] = achiev.find('h5').text
                    steam_achivements.append(achiev_dict)

                charts_url = self.charts_url.replace('{id}', steam_id)
                soup_charts = get_soup(charts_url, steam=True)
                try:
                    steam_atp = int(soup_charts.find_all('div', {'class': 'app-stat'})[-1].find('span').text)
                except Exception as _:
                    pass
            except Exception as _:
                pass
        
        return {'steam-description': steam_description, 'steam-summary': steam_summary, 'steam-tags': steam_tags, 'steam-raw': steam_raw,
                'steam-genres': steam_genres, 'steam-positive': steam_critics, 'steam-images': steam_images, 'steam-success': success,
                'steam-nb-users': steam_nb_users, 'steam-release-date': date, 'steam-developers': developers_list,
                'steam-all-time-peaks': steam_atp, 'steam-achievements': steam_achivements}

    def get_api_info(self, title):
        return super().get_api_info(title)
    
    def get_raw_info(self, url):
        success = False
        raw_info = ''
        try:
            soup = get_soup(url, steam=True)
            raw_info = str(soup.find('div', {'id': 'aboutThisGame'}))
            success = True
        except Exception as _:
            pass
        return {'steam-raw': raw_info, 'steam-success': success}
