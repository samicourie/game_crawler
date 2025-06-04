import urllib
import wikipediaapi
from crawlers.crawler import Crawler
from util.utility import get_soup, get_best_match


class WikipediaCrawler(Crawler):
    
    def __init__(self):
        super().__init__()
        self.base_wiki = 'https://en.wikipedia.org'
        self.wiki_obj = wikipediaapi.Wikipedia('Games DB', 'en')

    def get_url(self, title):
        temp_title = title
        # score, edist_score = 0, 0
        score = 0
        # url, edist_url = '', ''
        url = ''
        success = False
        try:
            new_title = title.replace(' ', '+')
            url = 'https://en.wikipedia.org/w/index.php?search=' + new_title + \
                    '+video+game&title=Special:Search&profile=advanced&fulltext=1&ns0=1'

            soup = get_soup(url)
            search_results = soup.find_all('div', {'class': 'mw-search-result-heading'})[:10]
            candidates = []
            urls = []
            for result in search_results:
                a_elem = result.find('a')
                search_title = a_elem.attrs['title']
                urls.append(urllib.parse.unquote((a_elem.attrs['href'])))
                candidates.append(search_title)

            best_candidate = get_best_match(candidates, title)
            temp_title = candidates[best_candidate[0]]
            score = best_candidate[1]
            url = self.base_wiki + urls[best_candidate[0]]
            success = True
        except Exception as _:
            pass

        return {'wikipedia-title': temp_title,
                'wikipedia-score': score, # 'wikipedia-edist-score': edist_score,
                'wikipedia-url': url, # 'wikipedia-edist-url': edist_url, 
                'wikipedia-success': success}


    def get_info(self, url, score):
        wiki_summary = '#'
        wiki_gameplay = '#'
        wiki_plot = '#'
        wiki_synopsis = '#'
        wiki_genre = '#'
        wiki_reception = '#'
        success = False
        if score >= self.accepted_score:
            soup = get_soup(url)
            try:
                new_genre_index = [d.text for d in soup.find_all('th', {'class': 'infobox-label'})].index('Genre(s)')
                new_genre = [d.text for d in soup.find_all('td', {'class': 'infobox-data'})][new_genre_index]
                wiki_genre = new_genre.replace(',', ';')
            except Exception as _:
                pass
            try:
                game_wiki_page = self.wiki_obj.page(url.split('wiki/')[1], unquote=True)
                wiki_summary = game_wiki_page.summary
            except Exception as _:
                pass

            wiki_gameplay = game_wiki_page.section_by_title('Gameplay')
            temp_text = ''
            if wiki_gameplay is not None:
                temp_text += wiki_gameplay.text
                if len(wiki_gameplay.sections) > 0:
                    for sec in wiki_gameplay.sections:
                        temp_text += sec.title + ': ' + sec.text + '\n'
            else:
                wiki_gameplay = '#'
            wiki_gameplay = temp_text

            temp_text = ''
            wiki_plot = game_wiki_page.section_by_title('Plot')
            if wiki_plot is not None:
                temp_text = wiki_plot.text
                if len(wiki_plot.sections) > 0:
                    for sec in wiki_plot.sections:
                        temp_text += sec.title + ': ' + sec.text + '\n'
            else:
                wiki_plot = '#'
            wiki_plot = temp_text

            temp_text = ''
            wiki_synopsis = game_wiki_page.section_by_title('Synopsis')
            if wiki_synopsis is not None:
                temp_text = wiki_synopsis.text
                if len(wiki_synopsis.sections) > 0:
                    for sec in wiki_synopsis.sections:
                        temp_text += sec.title + ': ' + sec.text + '\n'
            else:
                wiki_synopsis = '#'
            wiki_synopsis = temp_text

            temp_text = ''
            wiki_reception = game_wiki_page.section_by_title('Reception')
            if wiki_reception is not None:
                temp_text = wiki_reception.text
                if len(wiki_reception.sections) > 0:
                    for sec in wiki_reception.sections:
                        temp_text += sec.title + ': ' + sec.text + '\n'
            else:
                wiki_reception = '#'
            wiki_reception = temp_text
            success = True

        return {'wikipedia-summary': wiki_summary, 'wikipedia-gameplay': wiki_gameplay, 
                'wikipedia-success': success, 'wikipedia-plot': wiki_plot, 
                'wikipedia-synopsis': wiki_synopsis, 'wikipedia-genre': wiki_genre, 'wikipedia-reception': wiki_reception}

    def get_api_info(self, title):
        return super().get_api_info(title)
