import re
import time
import json
import copy
import random
import argparse
import string
import urllib
import asyncio
import requests
import unicodedata
import editdistance
from datetime import datetime

import rawg
import wikipediaapi
from bs4 import BeautifulSoup
from giantbomb import giantbomb
from howlongtobeatpy import HowLongToBeat
from util.config import IGDB_CLIENT_ID, IGDB_CLIENT_SECRET, IGDB_TOKEN, RAWG_KEY, GIANTBOMB_KEY

json_list = []
nb_images = 10
my_key = GIANTBOMB_KEY
rawg_key = RAWG_KEY
igdb_token = IGDB_TOKEN
igdb_client_id = IGDB_CLIENT_ID
igdb_client_secret = IGDB_CLIENT_SECRET
headers = {'Client-ID': igdb_client_id, 'Authorization': 'Bearer ' + igdb_token}

gb = giantbomb.Api(my_key, 'API test')
hltb = HowLongToBeat()
wiki_obj = wikipediaapi.Wikipedia('Games DB', 'en')
alphabet = list(string.ascii_uppercase)

base_meta = 'https://www.metacritic.com'
base_wiki = 'https://en.wikipedia.org'
base_riot = 'https://en.riotpixels.com'
base_hltb = 'https://howlongtobeat.com/game/'
base_backloggd = 'https://backloggd.com'

soup_headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) '
              'AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/50.0.2661.102 Safari/537.36'}
cookies = {'birthtime': '631148401'}

igdb_categories = {0: 'Main Game', 1: 'DLC', 2: 'Expansion', 3: 'Bundle', 4: 'Standalone Expansion',
                   5: 'Mod', 6: 'Episode', 7: 'Season', 8: 'Remake', 9: 'Remaster', 10: 'Expanded Game',
                   11: 'Port', 12: 'Fork', 13: 'Pack', 14: 'Update'}

names_dict = {'Giant Id': 'giantbomb-id', 'name': 'giantbomb-name', 'aliases': 'giantbomb-aliases', 'deck': 'giantbomb-intro',
              'description': 'giantbomb-description', 'platforms': 'giantbomb-platforms', 'developers': 'giantbomb-developers',
              'publishers': 'giantbomb-publishers', 'franchises': 'giantbomb-franchises', 'releases': 'giantbomb-releases', 'images': 'giantbomb-screenshots',
              'genres': 'giantbomb-genres', 'themes': 'giantbomb-themes', 'original_release_date': 'giantbomb-release-date',
              'similar_games': 'giantbomb-similar-games'}

words_subs = {'1': ['i', 'one', '1'], 'one': ['i', 'one', '1'], 'i': ['i', 'one', '1'],
              '2': ['ii', 'two', '2'], 'two': ['ii', 'two', '2'], 'ii': ['ii', 'two', '2'],
              '3': ['iii', 'three', '3'], 'three': ['iii', 'three', '3'], 'iii': ['iii', 'three', '3'],
              '4': ['iv', 'four', '4'], 'four': ['iv', 'four', '4'], 'iv': ['iv', 'four', '4'],
              '5': ['v', 'five', '5'], 'five': ['v', 'five', '5'], 'v': ['v', 'five', '5'],
              '6': ['vi', 'six', '6'], 'six': ['vi', 'six', '6'], 'vi': ['vi', 'six', '6'],
              '7': ['vii', 'seven', '7'], 'seven': ['vii', 'seven', '7'], 'vii': ['vii', 'seven', '7'],
              '8': ['viii', 'eight', '8'], 'eight': ['viii', 'eight', '8'], 'viii': ['viii', 'eight', '8'],
              '9': ['ix', 'nine', '9'], 'nine': ['ix', 'nine', '9'], 'ix': ['ix', 'nine', '9'],
              '10': ['x', 'ten', '10'], 'ten': ['x', 'ten', '10'], 'x': ['x', 'ten', '10']}

game_specials = ['platforms', 'genres', 'releases', 'themes', 'images']

def format_string(str_obj):
    str_obj = str_obj.replace('&', 'and')
    title_words = [v.translate(str.maketrans('', '', string.punctuation))
                       .lower().strip() for v in re.sub('/|_|-|:|™|®', ' ', str_obj).split(' ')]
    title_words = [unicodedata.normalize('NFKD', v).encode('ASCII', 'ignore').decode('utf-8')
                   for v in title_words if v != '']
    return title_words


def get_best_match(candidates, title):
    best_match = 0
    best_index = 0
    best_score = 0

    title_words = format_string(title)
    
    for ind, candidate in enumerate(candidates):

        temp_candidate = candidate.replace('video game', '')
        candidate_words = format_string(temp_candidate)
        
        nb_common_words = 0
        if len(title_words) < len(candidate_words):
            smaller_title = title_words
            bigger_title = copy.copy(candidate_words)
        else:
            smaller_title = candidate_words
            bigger_title = copy.copy(title_words)

        for word in smaller_title:
            if word in bigger_title:
                nb_common_words += 1
                bigger_title.remove(word)
            elif word in words_subs:
                for sub_word in words_subs[word]:
                    if sub_word in bigger_title:
                        nb_common_words += 1
                        bigger_title.remove(sub_word)
        max_length = max(len(title_words), len(candidate_words))
        nb_smaller_words = nb_common_words / len(smaller_title)
        nb_common_words /= max_length

        # score = (nb_smaller_words + nb_common_words) / 2
        if nb_common_words > best_match:
            best_match = nb_common_words
            best_score = nb_smaller_words
            best_index = ind

    return best_index, best_match, best_score


def get_best_edit_distance(candidates, title):
    best_index = 0
    best_score = 2000

    new_title = ' '.join(format_string(title))
    for ind, candidate in enumerate(candidates):

        temp_candidate = candidate.replace('video game', '')
        temp_candidate = ' '.join(format_string(temp_candidate))
        distance = editdistance.distance(new_title, temp_candidate)
        if distance < best_score:
            best_score = distance
            best_index = ind

    return best_index, best_score


def get_soup(url, steam=False):
    if steam:
        
        webpage = requests.get(url, headers=soup_headers, cookies=cookies)
    else:
        webpage = requests.get(url, headers=soup_headers)
    return BeautifulSoup(webpage.text, 'html.parser')


def get_steam_url(title):
    temp_title = title
    score, edist_score = 0, 0
    url, edist_url = '', ''
    success = True
    try:
        base_url = 'https://store.steampowered.com/search/?term='
        new_title = title.replace(' ', '+')
        url = base_url + new_title
        soup = get_soup(url)
        urls = []
        search_results = soup.find_all('a', {'class':
                                                ['search_result_row ds_collapse_flag', 'app_impression_tracked']})[:10]
        candidates = []
        for result in search_results:
            search_title = result.find('span', {'class': 'title'}).text
            urls.append(result.attrs['href'])
            candidates.append(search_title)

        best_candidate = get_best_match(candidates, title)
        temp_title = candidates[best_candidate[0]]
        score = best_candidate[1]
        url = urls[best_candidate[0]]
        
        best_edist_candidate = get_best_edit_distance(candidates, title)
        edist_url = urls[best_edist_candidate[0]]
        edist_score = best_edist_candidate[1]

    except Exception as e:
        success = False

    return {'steam-title': temp_title,
            'steam-score': score, 'steam-edist-score': edist_score,
            'steam-url': url, 'steam-edist-url': edist_url,'steam-success': success}


def get_meta_url(title):
    temp_title = title
    score, edist_score = 0, 0
    url, edist_url = '', ''
    success = True

    try:
        base_url = 'https://www.metacritic.com/search/'
        new_title = title
        url = base_url + new_title + '/?page=1&category=13'

        soup = get_soup(url)
        search_results = soup.find_all('a', {'class': 'c-pageSiteSearch-results-item'})[:15]
        candidates = []
        urls = []
        for result in search_results:
            p_elem = result.find('p')
            search_title = p_elem.text.strip()
            search_title = re.sub(' +', ' ', search_title)
            search_title = search_title.replace('\n', '')
            if 'ios' in result.attrs['href'] or 'xbox' in result.attrs['href']:
                continue
            urls.append(base_meta + result.attrs['href'])
            candidates.append(search_title)

        best_candidate = get_best_match(candidates, title)
        temp_title = candidates[best_candidate[0]]
        score = best_candidate[1]
        url = urls[best_candidate[0]]

        best_edist_candidate = get_best_edit_distance(candidates, title)
        edist_url = urls[best_edist_candidate[0]]
        edist_score = best_edist_candidate[1]
    except Exception as _:
        success = False
    
    return {'metacritics-title': temp_title,
            'metacritics-score': score, 'metacritics-edist-score': edist_score,
            'metacritics-url': url, 'metacritics-edist-url': edist_url, 'metacritics-success': success}


def get_wiki_url(title):
    temp_title = title
    score, edist_score = 0, 0
    url, edist_url = '', ''
    success = True
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
        url = base_wiki + urls[best_candidate[0]]

        best_edist_candidate = get_best_edit_distance(candidates, title)
        edist_url = base_wiki + urls[best_edist_candidate[0]]
        edist_score = best_edist_candidate[1]
    except Exception as _:
        success = False

    return {'wikipedia-title': temp_title,
            'wikipedia-score': score, 'wikipedia-edist-score': edist_score,
            'wikipedia-url': url, 'wikipedia-edist-url': edist_url, 'wikipedia-success': success}


def get_gameplay_time(title):
    main = '/'
    main_extra = '/'
    complete = '/'
    candidates = []
    clean_title = title.replace('-', '')
    try:
        hltb_games = hltb.search(clean_title, similarity_case_sensitive=False)
        for game in hltb_games:
            if game.similarity > 0.7:
                candidates.append(game.game_name)

        best_candidate = hltb_games[get_best_match(candidates, title)[0]]
        main = best_candidate.main_story
        main_extra = best_candidate.main_extra
        complete = best_candidate.completionist
    except Exception as e:
        pass
    return {'hltb-main': main, 'hltb-main+': main_extra, 'hltb-complete': complete}


def get_backloggd_url(title):
    temp_title = title
    score = 0
    url = ''
    success = True
    try:
        new_title = title.replace('-', ' ').strip()
        new_title = re.sub(' +', ' ', new_title)
        url = base_backloggd + '/search/games/' + new_title + '/'
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
        temp_title = candidates_titles[best_candidate[0]]
        score = best_candidate[1]
        url = base_backloggd + candidates_urls[best_candidate[0]]

    except Exception as _:
        success = False

    return {'backloggd-title': temp_title,
            'backloggd-score': score,
            'backloggd-url': url, 'backloggd-success': success}


def get_riot_url(title):
    temp_title = title
    score = 0
    url = ''
    success = True
    try:
        new_title = title.replace('-', ' ').strip()
        new_title = re.sub(' +', ' ', new_title)
        new_title = new_title.replace(' ', '&')
        url = base_riot + '/search/' + new_title + '/'
        soup = get_soup(url)
        candidates = json.loads(soup.text)
        candidates_titles = [v['value'] for v in candidates]
        best_candidate = get_best_match(candidates_titles, title)

        temp_title = candidates[best_candidate[0]]['value']
        score = best_candidate[1]
        url = base_riot + '/games/' + candidates[best_candidate[0]]['id'].replace('games-', '') + '/screenshots/'

    except Exception as _:
        success = False

    return {'riot-title': temp_title,
            'riot-score': score,
            'riot-url': url, 'riot-success': success}


async def get_rawg_requests(title):
    temp_title = title
    score = 0
    description = ''
    success = True
    async with rawg.ApiClient(rawg.Configuration(api_key={'key': rawg_key})) as api_client:
        # Create an instance of the API class
        try:
            api = rawg.GamesApi(api_client)
            
            # Making requests
            coros = [api.games_read(id=name) for name in [title]]

            candidates_obj = []

            # Waiting for requests
            for coro in asyncio.as_completed(coros):
                game: rawg.GameSingle = await coro
                candidates_obj.append({'id': game.id, 'name': game.name, 'description': game.description})
            
            candidates = [g['name'] for g in candidates_obj]
            best_candidate = get_best_match(candidates, title)

            temp_title = candidates_obj[best_candidate[0]]['name']
            score = best_candidate[1]
            description = candidates_obj[best_candidate[0]]['description']
            
        except Exception as _:
            success = False
    
    return {'rawg-title': temp_title,
            'rawg-score': score, 'rawg-success': success,
            'rawg-description': description}


def get_giantbomb_info(title):
    json_obj = {}
    success = True
    try:
        response = gb.search(title)
        candidates = [v.name for v in response]
        best_index, best_match, best_score = get_best_match(candidates, title)
        if best_match > 0.7:
            giant_id = response[best_index].id
            game = gb.get_game(giant_id)
            game_attrs = vars(game)
            game_attrs['title'] = title
            game_attrs['Giant Id'] = giant_id
            game_attrs['image'] = vars(game_attrs['image'])
            for key in game_specials:
                special_obj = game_attrs[key]
                if special_obj is not None:
                    game_attrs[key] = [vars(v) for v in special_obj]

            for k, v in game_attrs.items():
                if k in names_dict:
                    if k in ['platforms', 'developers', 'publishers', 'franchises', 'releases', 'themes', 'genres'] and game_attrs[k] is not None:
                        json_obj[names_dict[k]] = '; '.join([obj['name'] for obj in v])
                    elif k == 'images' and game_attrs[k] is not None:
                        json_obj[names_dict[k]] = [obj['super_url'].replace('scale_large', 'original') for obj in v]
                    elif k == 'similar_games' and game_attrs[k] is not None:
                        json_obj[names_dict[k]] = [{obj['name']: obj['id']} for obj in v]
                        json_obj['giantbomb-similar-titles'] = '; '.join([obj['name'] for obj in v])
                    elif k == 'description' and game_attrs[k] is not None:
                        json_obj[names_dict[k]] = BeautifulSoup(v, 'html.parser').get_text(' ')
                    else:
                        json_obj[names_dict[k]] = v
            for k, v in json_obj.items():
                json_obj[k] = v if v is not None else ''
        else:
            success = False
    except Exception as e:
        success = False
    json_obj['giantbomb-success'] = success
    return json_obj


def search_igdb(title, query=None):
    success = True
    best_search_name = ''
    best_search_id = ''
    best_score = 0

    best_edist_name = ''
    best_edist_score = 0
    best_edist_id = ''

    if query is None:
        query = '"; fields name; where platforms.category!=(3); limit 30;'

    try:
        search_query = 'search "' + title + query
        response = requests.post('https://api.igdb.com/v4/games', headers=headers, data=search_query)
        search_results = json.loads(response.content.decode('utf-8'))
        candidates = [v['name'] for v in search_results]
        best_match = get_best_match(candidates=candidates, title=title)
        best_search_name = search_results[best_match[0]]['name']
        best_search_id = search_results[best_match[0]]['id']
        best_score = best_match[1]
        best_edist_match = get_best_edit_distance(candidates=candidates, title=title)
        best_edist_name = search_results[best_edist_match[0]]['name']
        best_edist_id = search_results[best_edist_match[0]]['id']
        best_edist_score = best_edist_match[1]
    except Exception as e:
        success = False
    return {'igdb-title': best_search_name, 'igdb-url': best_search_id, 'igdb-score': best_score,
            'igdb-edist-title': best_edist_name, 'igdb-edist-url': best_edist_id, 'igdb-edist-score': best_edist_score, 'igdb-success': success}


def get_igdb_info(game_id, score=0):
    igdb_dict = {'igdb-id': game_id, 'igdb-success': True}
    if score > 0.75:
        try:
            query = 'fields name,alternative_names.name,game_engines.name,artworks.url,similar_games.name, remakes.name, remasters.name,'\
                    'cover.url,dlcs.name,expansions.name,first_release_date,player_perspectives.name,screenshots.url,standalone_expansions.name,'\
                    'franchise.name,themes.name,keywords.name,screenshots.url,category,rating,genres.name,summary,storyline;'
            
            response = requests.post('https://api.igdb.com/v4/games', headers=headers, data=query + ' where id=' + str(game_id) + ';')
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
                igdb_dict['igdb-category'] = igdb_categories[game['category']]
            if 'cover' in game:
                igdb_dict['igdb-cover'] = 'https:' + game['cover']['url'].replace('t_thumb', 't_1080p')
            if 'first_release_date' in game:
                igdb_dict['igdb-release-date'] =  datetime.fromtimestamp(game['first_release_date']).strftime('%d %b, %Y')
                
        except Exception as _:
            igdb_dict['igdb-success'] = False
    else:
        igdb_dict['igdb-success'] = False
    return igdb_dict


def get_wiki_info(url, score):
    wiki_summary = '#'
    wiki_gameplay = '#'
    wiki_plot = '#'
    wiki_synopsis = '#'
    wiki_genre = '#'
    success = True
    if score >= 0.7:
        soup = get_soup(url)
        try:
            new_genre_index = [d.text for d in soup.find_all('th', {'class': 'infobox-label'})].index('Genre(s)')
            new_genre = [d.text for d in soup.find_all('td', {'class': 'infobox-data'})][new_genre_index]
            wiki_genre = new_genre.replace(',', ';')
        except Exception as e:
            pass
        try:
            game_wiki_page = wiki_obj.page(url.split('wiki/')[1], unquote=True)
            wiki_summary = game_wiki_page.summary
        except Exception as e:
            success = False

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
    else:
        success = False

    return {'wikipedia-summary': wiki_summary, 'wikipedia-gameplay': wiki_gameplay, 'wikipedia-success': success,
            'wikipedia-plot': wiki_plot, 'wikipedia-synopsis': wiki_synopsis, 'wikipedia-genre': wiki_genre}


def get_steam_info(url, score):
    steam_score = float(score)

    steam_description = '#'
    steam_summary = '#'
    steam_critics = ''
    steam_tags = '#'
    steam_nb_users = ''
    steam_genres = '#'
    developers_list = ''
    date = ''
    success = True
    steam_images = []
    if steam_score >= 0.7:
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
                steam_summary = steam_summary.text
                steam_summary = steam_summary.replace('\r', ' ')
                steam_summary = steam_summary.replace('\t', ' ')
                steam_summary = steam_summary.replace('\n', ' ')
                steam_summary = steam_summary.replace("\'", "'")
                steam_summary = steam_summary.strip()
                steam_summary = re.sub(' +', ' ', steam_summary)
            else:
                steam_summary = '#'

            mydivs = soup.find_all('div', {'class': 'user_reviews_summary_row'})
            if len(mydivs) > 2:
                wanted_div = mydivs[1]

            else:
                wanted_div = mydivs[0]
            steam_critics = wanted_div.attrs['data-tooltip-html'].split('%')[0]
            steam_nb_users = int(wanted_div.find('span', {'class': 'responsive_hidden'})
                                    .text[1:-1].strip()[1:-1].replace(',', ''))
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

        except Exception as _:
            success = False
    else:
        success = False
    
    return {'steam-description': steam_description, 'steam-summary': steam_summary, 'steam-tags': steam_tags,
            'steam-genres': steam_genres, 'steam-positive': steam_critics, 'steam-images': steam_images, 'steam-success': success,
            'steam-nb-users': steam_nb_users, 'steam-release-date': date, 'steam-developers': developers_list}


def get_meta_info(url, score):
    meta_score = float(score)
    meta_description = '#'
    critics = ''
    users = ''
    date = ''
    success = True

    if meta_score >= 0.75:
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
        except Exception as _:
            success = False
    else:
        success = False
    
    return {'metacritics-description': meta_description, 'metacritics-success': success,
            'metacritics-critics': critics, 'metacritics-users': users, 'metacritics-release-date': date}


def get_backloggd_info(url, score):
    backloggd_score = float(score)
    backloggd_description = '#'
    backloggd_rating = ''
    split_ratings = ''
    success = True

    if backloggd_score >= 0.75:
        try:
            soup = get_soup(url)
            backloggd_description = soup.find('div', {'id': 'collapseSummary'}).text
            backloggd_rating = soup.find('div', {'id': 'game-rating'}).find('h1').text
            side_content = soup.find('div', {'class': 'side-section'}).find_all('div', {'class': 'col px-0 top-tooltip'})
            ratings = [v.attrs['data-tippy-content'] for v in side_content]
            count_ratings = [v.split(' ★ ')[0] for v in ratings]
            split_ratings = {v.split(' | ')[1]: v.split(' | ')[0] for v in count_ratings}
        except Exception as _:
            success = False
    else:
        success = False
    
    return {'backloggd-description': backloggd_description, 'backloggd-success': success, 
            'backloggd-rating': backloggd_rating, 'backloggd-split-rating': split_ratings}


def get_riot_info(url, score):
    riot_score = float(score)
    riot_images = []
    success = True

    if riot_score >= 0.7:
        try:
            soup = get_soup(url)
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
        except Exception as _:
            success = False
    else:
        success = False
    
    return {'riot-screenshots': riot_images, 'riot-success': success}


def get_rawg_info(temp_title):
    rawg_title = re.sub(r'[^a-zA-Z0-9- ]', '', temp_title)
    rawg_title = rawg_title.lower().replace(' ', '-')
    while '--' in rawg_title:
        rawg_title = rawg_title.replace('--', '-')
    rawg_obj = asyncio.get_event_loop().run_until_complete(get_rawg_requests(rawg_title))
    return rawg_obj


def get_images(game_obj):
    image_nb = 1
    folder = game_obj['title'][0][0].upper()
    if folder not in alphabet:
        folder = '#'
    image_list = []
    
    # images_path = 'Pictures/' + folder + '/' + title + '_'
    images_path = 'Pictures/Test/' + game_obj['title'] + '_'
    image_list.extend(game_obj.get('steam-images', []))
    image_list.extend(game_obj.get('igdb-screenshots', []))
    image_list.extend(game_obj.get('riot-screenshots', []))
    image_list.extend(game_obj.get('giantbomb-screenshots', []))

    for sc_src in random.sample(image_list, nb_images):
        try:
            response = requests.get(sc_src)
            with open(images_path + str(image_nb) + '.jpg', 'wb') as img_file:
                    img_file.write(response.content)
        except Exception as _:
            continue

    image_nb = 1
    for sc_src in game_obj.get('igdb-artworks', []):
        try:
            response = requests.get(sc_src)
            with open(images_path + str(image_nb) + '_ART.jpg', 'wb') as img_file:
                    img_file.write(response.content)
        except Exception as _:
            continue
    
    if 'igdb-cover' in game_obj:
        try:
            response = requests.get(game_obj['igdb-cover'], images_path + 'Cover.jpg')
            with open(images_path.replace(':', ' -') + 'Cover.jpg', 'wb') as img_file:
                img_file.write(response.content)
        except Exception as _:
            pass


def generate_text(game_obj):
    text_obj = dict()
    str_obj = ''
    steam_dict = {'steam-description': 'Description: ', 'steam-summary': 'Summary: ',
                  'steam-tags': 'Tags: ', 'steam-genres': 'Genres: '}
    for key in steam_dict:
        if game_obj.get(key, '#') != '#':
            str_obj += steam_dict[key] + game_obj[key] + '\n'
    if str_obj != '':
        text_obj['text-steam'] = 'Steam: \n' + str_obj
    
    if game_obj.get('metacritics-description', '#') != '#':
        text_obj['text-metacritics'] = 'Metacritic: \n' + game_obj['metacritics-description']  + '\n'

    if game_obj.get('rawg-description', '#') != '#':
        text_obj['text-rawg'] = 'RAWG: \n' + game_obj['rawg-description']  + '\n'
    
    str_obj = ''
    wiki_dict = {'wikipedia-summary': 'Summary: ', 'wikipedia-gameplay': 'Gameplay: ',
                  'wikipedia-plot': 'Plot: ', 'wikipedia-synopsis': 'Synopsis: ',
                  'wikipedia-genre': 'Genres: '}
    for key in wiki_dict:
        if game_obj.get(key, '#') != '#':
            str_obj += wiki_dict[key] + game_obj[key] + '\n'
    if str_obj != '':
        text_obj['text-wikipedia'] = 'Wikipedia: \n' + str_obj

    str_obj = ''
    gantbomb_dict = {'giantbomb-intro': 'Intro: ', 'giantbomb-description': 'Description: ',
                     'giantbomb-genres': 'Genres: ', 'giantbomb-themes': 'Themes: '}
    for key in gantbomb_dict:
        if game_obj.get(key, '#') != '#':
            str_obj += gantbomb_dict[key] + game_obj[key] + '\n'
    if str_obj != '':
        text_obj['text-giantbomb'] = 'GiantBomb: \n' + str_obj

    str_obj = ''
    igdb_dict = {'igdb-summary': 'Summary: ', 'igdb-storyline': 'Story: ',
                 'igdb-genres': 'Genres: ', 'igdb-themes': 'Themes: ',
                 'igdb-keywords': 'Keywords: ', 'igdb-perspectives': 'Perspectives: '}
    for key in igdb_dict:
        if game_obj.get(key, '#') != '#':
            str_obj += igdb_dict[key] + game_obj[key] + '\n'
    if str_obj != '':
        text_obj['text-igdb'] = 'IGDB: \n' + str_obj

    if game_obj.get('backloggd-description', '#') != '#':
        text_obj['text-backloggd'] = 'Backloggd: \n' + game_obj['backloggd-description']  + '\n'

    return text_obj


if __name__ == '__main__':
    ultimate_games_dict = dict()
    ultimate_text_dict = dict()
    nb_screenshots = 0
    existed_games = []

    sites_funcs = {'wikipedia': get_wiki_url, 'steam': get_steam_url, 'riot': get_riot_url,
                   'metacritics': get_meta_url, 'backloggd': get_backloggd_url,
                   'igdb': search_igdb, 'giantbomb': get_giantbomb_info,
                   'hltb': get_gameplay_time, 'rawg': get_rawg_info}
    crawl_funcs = {'wikipedia': get_wiki_info, 'steam': get_steam_info, 'riot': get_riot_info,
                  'metacritics': get_meta_info, 'igdb': get_igdb_info, 'backloggd': get_backloggd_info}
    
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('-i', '--input_file', type=str, help='Path to new games file', default='new_games.txt')
    parser.add_argument('-s', '--sites', type=str, help='site to crawl separated by (,)',
                        default='wikipedia,steam,igdb,giantbomb,rawg,hltb,metacritics,backloggd')
    parser.add_argument('-m', '--images', type=bool, help='Whether to download game images or not (slow)', default=False)
    parser.add_argument('-o', '--output_prefix', type=str, help='Prefix of output files', default='new_games_')
    args = parser.parse_args()

    with open(args.input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    sites = args.sites.split(',')

    for ind, line in enumerate(lines):
        temp_line = line.replace('\n', '')
        gb_name = temp_line
        modification_date = datetime.now()
        modification_date = modification_date.strftime('%d %b, %Y')
        version_date = modification_date
        if ' $ ' in temp_line:
            split_list = temp_line.split(' $ ')
            temp_line = split_list[0]
            gb_name = split_list[1]
        if ' # ' in temp_line:
            split_list = temp_line.split(' # ')
            temp_line = split_list[0]
            version_date = split_list[1]

        try:
            ultimate_games_dict[temp_line] = {'title': temp_line}
            ultimate_text_dict[temp_line] = dict()

            # print('Crawling for', temp_line)
            for site in sites:
                if site in sites_funcs:
                    # print('Crawling', site)
                    ultimate_games_dict[temp_line].update(sites_funcs[site](temp_line))
            
            if 'giantbomb' in sites or 'metacritics' in sites:
                # print('Sleeping ...')
                time.sleep(30)
            else:
                time.sleep(1)

            sites_success = ''
            for site in sites:
                if site in crawl_funcs:
                    if ultimate_games_dict[temp_line].get(site+'-success', False):
                        site_info = crawl_funcs[site](ultimate_games_dict[temp_line][site+'-url'],
                                                       score=ultimate_games_dict[temp_line][site+'-score'])
                        if site_info[site+'-success']:
                            ultimate_games_dict[temp_line].update(site_info)
                        else:
                            ultimate_games_dict[temp_line][site+'-success'] = False
                    else:
                        ultimate_games_dict[temp_line][site+'-success'] = False
                    sites_success += site + ': ' + str(ultimate_games_dict[temp_line][site+'-success']) + ' # '
            if args.images:
                image_count = get_images(ultimate_games_dict[temp_line])
            
            print('Success:', ind, temp_line)
            
        except Exception as e:
            print(' Error:', temp_line, e)
        
        if 'giantbomb' in sites or 'metacritics' in sites:
            # print('Sleeping ...')
            time.sleep(30)
        else:
            time.sleep(1)

        ultimate_text_dict[temp_line].update(generate_text(ultimate_games_dict[temp_line]))

    with open(args.output_prefix + 'info.json', 'w', encoding='utf-8') as file:
        json.dump(ultimate_games_dict, file)
        
    with open(args.output_prefix + 'text.json', 'w', encoding='utf-8') as file:
        json.dump(ultimate_text_dict, file)
