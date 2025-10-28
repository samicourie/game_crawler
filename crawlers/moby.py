import zlib
import json
from crawlers.crawler import Crawler
from util.utility import get_soup, get_best_match

class MobyCrawler(Crawler):

    def __init__(self):
        super().__init__()
        self.site = 'moby'
        self.base_moby = 'https://www.mobygames.com/search/?q='

    def get_url(self, title, year=0):
        temp_title = title
        # score, edist_score = 0, 0
        # url, edist_url = '', ''
        score = 0
        url = ''
        success = False
        try:
            
            url = self.base_moby + temp_title
            soup = get_soup(url, cloud_scrapper=True)
            urls = []
            table_elem = soup.find_all('table')[0]
            search_results = table_elem.find_all('b')
            candidates = []
            candidates_years = []
            for result in search_results:
                search_title = result.text
                urls.append(result.find('a').attrs['href'])
                candidates.append(search_title)
                year_spans = result.parent.find_all('span')
                try:
                    if len(year_spans) > 1:
                        if ',' in year_spans[1].text:
                            candidates_years.append(int(year_spans[1].text.split(', ')[1].replace(')', '')))
                        else:
                            candidates_years.append(int(year_spans[1].text[1:].replace(')', '')))
                    else:
                        candidates_years.append(0)
                except Exception as _:
                    candidates_years.append(0)

            best_candidate = get_best_match(candidates, title, title_year=year, candidates_years=candidates_years)
            temp_title = candidates[best_candidate[0]]
            score = best_candidate[1]
            url = urls[best_candidate[0]]
            if score >= self.accepted_score:
                success = True
        except Exception as _:
            pass

        return {'moby-title': temp_title,
                'moby-score': score, # 'moby-edist-score': edist_score,
                'moby-url': url, # 'moby-edist-url': edist_url,
                'moby-success': success}
    

    def get_info(self, url, score):
        soup = get_soup(url, cloud_scrapper=True)
        json_obj = {'moby-success': False}

        try:
            if score >= self.accepted_score:
                title_elem = soup.find('h1', {'class': 'mb-0'})
                json_obj['moby-title'] = title_elem.text
                next_elem = title_elem.find_next('div')
                if 'aka' in next_elem.text:
                    json_obj['moby-aliases'] = next_elem.text.split('aka:\n')[1].strip()
                    next_elem = next_elem.find_next('div')
                json_obj['moby-id'] = url.split('/')[4]

                temp_div = soup.find('div', {'class': 'info-release'})
                temp_dl = temp_div.find('dl')
                temp_elems = temp_dl.find_all(recursive=False)
                for el in range(0, len(temp_elems), 2):
                    dt_elem = temp_elems[el].text
                    dd_elem = temp_elems[el+1].text
                    if 'Released' in dt_elem:
                        json_obj['moby-release-date'] = dd_elem.split('on')[0].strip()
                        continue
                    if 'Publishers' in dt_elem:
                        json_obj['moby-publishers'] = dd_elem.strip()
                        continue
                    if 'Developers' in dt_elem:
                        json_obj['moby-developers'] = dd_elem.strip()
                        continue

                temp_div = soup.find('div', {'class': 'info-score'})
                temp_dl = temp_div.find('dl')
                temp_elems = temp_dl.find_all(recursive=False)
                for el in range(0, len(temp_elems), 2):
                    dt_elem = temp_elems[el].text
                    dd_elem = temp_elems[el+1].text
                    if 'Moby Score' in dt_elem:
                        try:
                            dd_split = dd_elem.split('#')
                            json_obj['moby-internal-score'] = dd_split[0].strip()
                            json_obj['moby-rank'] = dd_split[1].split(' of')[0].strip()
                            continue
                        except Exception as _:
                            pass
                    if 'Critics' in dt_elem:
                        try:
                            dd_split = dd_elem.split('%')
                            json_obj['moby-critics-score'] = dd_split[0].strip()
                            json_obj['moby-critics-count'] = dd_split[1].replace('(', '').replace(')', '').strip()
                            continue
                        except Exception as _:
                            pass

                temp_div = soup.find('div', {'class': 'info-genres'})
                temp_dl = temp_div.find('dl')
                temp_elems = temp_dl.find_all(recursive=False)
                genre_dict = dict()
                for el in range(0, len(temp_elems), 2):
                    dt_elem = temp_elems[el].text
                    dd_elem = temp_elems[el+1].get_text(' ; ')
                    genre_dict[dt_elem] = dd_elem
                json_obj['moby-genres'] = genre_dict

                try:
                    description = soup.find('section', {'id': 'gameOfficialDescription'}).text.replace('\n\n', '\n').strip()
                except AttributeError as _:
                    description = soup.find('section', {'id': 'gameDescription'}).text.replace('\n\n', '\n').strip()
                    
                json_obj['moby-description'] = description
                # json_obj['moby-raw'] = zlib.compress(self.get_raw_info(soup).encode('utf-8'))
                json_obj['moby-raw'] = self.get_raw_info(soup)

                tags_elem = soup.find('section', {'id': 'gameGroups'})
                tags_li = tags_elem.find_all('li')
                json_obj['moby-tags'] = ' ; '.join([v.text.strip() for v in tags_li])

                review_section = soup.find('section', {'id': 'critic-reviews'})
                reviews_elem = json.loads(str(review_section.find('critic-reviews').attrs.get(':reviews')))
                reviews_dict = dict()
                for review in reviews_elem:
                    journal = review['source']['name']
                    if journal not in reviews_dict:
                        reviews_dict[journal] = []
                    reviews_dict[journal].append({'review': review['citation'], 'score': review['normalized_score']}) 
                json_obj['moby-reviews'] = reviews_dict

                images = self.get_moby_screenshots(url)
                if images and len(images) > 0:
                    json_obj['moby-screenshots'] = images

                json_obj['moby-success'] = True
        except Exception as _:
            pass

        return json_obj

    def get_moby_screenshots(self, url):
        temp_url = url + '/screenshots/'
        soup = get_soup(temp_url, cloud_scrapper=True)
        images = []
        
        sc_div = soup.find('div', {'class': 'img-holder mb'})
        if sc_div:
            figures = sc_div.find_all('figure')
            try:
                for fig in figures:
                    images.append({'url': fig.find('img').attrs['src'].replace('.webp', '.jpg'), 'caption': fig.find('figcaption').text.strip()})
            except Exception as _:
                pass
        return images


    def get_api_info(self, title):
        return super().get_api_info(title)
    
    def get_raw_info(self, soup):
        success = False
        raw_info = ''

        try:
            description_section = soup.find('section', {'id': 'gameDescription'})
            raw_info = ' '.join([str(v) for v in description_section.contents])
            success = True
        except Exception as _:
            pass

        if not success:
            try:
                
                arrow_elem = soup.find('summary', {'class': 'no-select text-bold'})
                if arrow_elem is not None:
                    arrow_elem.decompose()
                raw_info = ' '.join([str(v) for v in soup.find('details', {'class': 'mb'}).contents])
                success = True
                
            except Exception as _:
                pass
        return raw_info
