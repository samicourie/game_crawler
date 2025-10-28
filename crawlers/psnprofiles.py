import re
from crawlers.crawler import Crawler
from util.utility import get_soup, get_best_match

class PSNProfilesCrawler(Crawler):

    def __init__(self):
        super().__init__()
        self.site = 'psnprofiles'
        self.base_psnprofiles = 'https://psnprofiles.com'

    def get_url(self, title, year=0):
        temp_title = title
        # score, edist_score = 0, 0
        # url, edist_url = '', ''
        score = 0
        url = ''
        success = False

        try:
            base_url = 'https://psnprofiles.com/search?q='
            new_title = title
            url = base_url + new_title

            soup = get_soup(url, cloud_scrapper=True)
            search_results = soup.find_all('a', {'class': 'title'})
            candidates = []
            urls = []
            for result in search_results:
                search_title = result.text.strip()
                urls.append(self.base_psnprofiles + result.attrs['href'])
                candidates.append(search_title)

            best_candidate = get_best_match(candidates, title, title_year=0)
            temp_title = candidates[best_candidate[0]]
            score = best_candidate[1]
            url = urls[best_candidate[0]]
            if score >= self.accepted_score:
                success = True
        except Exception as _:
            pass

        return {'psnprofiles-title': temp_title,
                'psnprofiles-score': score, # 'metacritics-edist-score': edist_score,
                'psnprofiles-url': url, # 'metacritics-edist-url': edist_url, 
                'psnprofiles-success': success}


    def get_info(self, url, score):
        psnprofiles_score = float(score)
        psnprofiles_achievements = []
        res_dict = {'psnprofiles-success': False}
        if psnprofiles_score >= self.accepted_score:
            try:
                soup = get_soup(url, cloud_scrapper=True)
                main_div = soup.find('div', {'class': 'col-xs'})
                ach_tables = main_div.find_all('table', {'class': 'zebra'})
                if len(ach_tables) > 1:
                    ach_tables = ach_tables[1:]

                for table in ach_tables:
                    ach_table_rows = table.find_all('tr')
                    if not ach_table_rows or len(ach_table_rows) == 0:
                        continue
                    if len(ach_table_rows) == 1:
                        temp_ach = dict()
                        row = ach_table_rows[0]
                        temp_ach['image'] = row.find('picture', {'class': 'game'}).find('img').attrs['src']
                        title_a = row.find('span', {'class': 'title'})
                        temp_ach['title'] = title_a.text.strip()
                        psnprofiles_achievements.append(temp_ach)
                        continue

                    for row in ach_table_rows:
                        try:
                            temp_ach = dict()
                            temp_ach['image'] = row.find('picture', {'class': 'trophy unearned unowned'}).find('img').attrs['src']
                            title_a = row.find('a', {'class': 'title'})
                            temp_ach['title'] = title_a.text.strip()
                            temp_ach['text'] = title_a.parent.text.replace(temp_ach['title'], '', 1).strip()
                            info_td = row.find('td', {'class': 'hover-hide'})
                            temp_ach['percentage'] = info_td.find('span', {'class': 'typo-top'}).text.strip()
                            temp_ach['rarity'] = info_td.find('span', {'class': 'typo-bottom'}).text.strip()
                            info_td = row.find('td', {'class': 'hover-show'})
                            temp_ach['percentage-2'] = info_td.find('span', {'class': 'typo-top'}).text.strip()
                            temp_ach['rarity-2'] = info_td.find('span', {'class': 'typo-bottom'}).text.strip()
                            td_images = row.find_all('img')
                            for img in td_images:
                                if 'title' in img.attrs:
                                    temp_ach['trophy'] = img.attrs['title']
                            psnprofiles_achievements.append(temp_ach)
                        except Exception as _:
                            pass
                    res_dict['psnprofiles-success'] = True
            except Exception as _:
                pass
        
        if len(psnprofiles_achievements) > 0:
            res_dict['psnprofiles-achievements'] = psnprofiles_achievements
        else:
            res_dict['psnprofiles-success'] = False

        return res_dict

    def get_api_info(self, title):
        return super().get_api_info(title)

    def get_raw_info(self, url):
        return super().get_raw_info(url)
