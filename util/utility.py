import os
import re
import zlib
import copy
import string
import pymongo
import requests
import unicodedata
import cloudscraper
from bs4 import BeautifulSoup


alphabet = list(string.ascii_uppercase)

headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) '
              'AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/50.0.2661.102 Safari/537.36'}
cookies = {'birthtime': '631148401'}


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


def remove_parenthesized_year(title):
    return re.sub(r'\(\d{4}\)', '', title).strip()


def format_string(str_obj):
    str_obj = str_obj.replace('&', 'and')
    title_words = [v.translate(str.maketrans('', '', string.punctuation))
                       .lower().strip() for v in re.sub('/|_|-|:|™|®', ' ', str_obj).split(' ')]
    title_words = [unicodedata.normalize('NFKD', v).encode('ASCII', 'ignore').decode('utf-8')
                   for v in title_words if v != '']
    return title_words


def get_best_match(candidates, title, title_year=0, candidates_years=None):
    best_match = 0
    best_index = 0
    best_score = 0
    best_year = 100
    title_year = int(title_year)
    title_words = format_string(title)
    
    for ind, candidate in enumerate(candidates):
        
        try:
            temp_candidate = candidate.replace('video game', '')
            temp_candidate = remove_parenthesized_year(temp_candidate)
            candidate_year = int(candidates_years[ind]) if candidates_years is not None else 0
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
                best_year = abs(title_year - candidate_year)
            elif nb_common_words == best_match:
                temp_year = abs(title_year - candidate_year)
                if temp_year < best_year:
                    best_year = temp_year
                    best_match = nb_common_words
                    best_score = nb_smaller_words
                    best_index = ind

        except Exception as _:
            continue

    return best_index, best_match, best_score


def get_soup(url, cloud_scrapper=False, steam=False):
    if steam:
        webpage = requests.get(url, headers=headers, cookies=cookies)
    elif cloud_scrapper:
        scraper = cloudscraper.create_scraper()
        webpage = scraper.get(url, headers=headers)
    else:
        webpage = requests.get(url, headers=headers)
    return BeautifulSoup(webpage.text, 'html.parser')


def get_mongo_collection():
    myclient = pymongo.MongoClient('mongodb://localhost:27017/')
    mycol = myclient['local']['MyGames']
    return mycol


def get_raw_collection():
    myclient = pymongo.MongoClient('mongodb://localhost:27017/')
    mycol = myclient['local']['MyRawGames']
    return mycol


def get_path(game_title, all_games_abbrv):

    min_length = 6

    if len(game_title) < min_length and game_title not in all_games_abbrv:
        return game_title

    letter_count = 2
    cleaned_game = re.sub(r'[^a-zA-Z0-9Ééöä]', ' ', game_title)
    cleaned_game = cleaned_game.strip()
    while True:
        game_abbr = ''
        for word in cleaned_game.split(' '):
            if word.isalpha():
                game_abbr += word[0:letter_count]
                continue
            if word.isnumeric() or word.isalnum() or word.replace(',', '').isnumeric():
                game_abbr += word
        if game_abbr.lower() in all_games_abbrv:
            letter_count += 1
        else:
            break
    
    return game_abbr


def get_score_color(score, score_base):
    try:
        if score >= (score_base*0.9):
            return 'purple'
        if score >= (score_base*0.8):
            return 'darkgreen'
        if score >= (score_base*0.7):
            return 'green'
        if score >= (score_base*0.6):
            return 'yellow'
        if score >= (score_base*0.5):
            return 'orange'
        if score >= (score_base*0.4):
            return 'red'
    except Exception as _:
        pass
    return 'red'
    

def organise_game_data(game_obj, all_games):
    new_obj = dict()

    genres = set()
    similar_games = []
    release_date = []
    new_obj['sites'] = set()
    scores = dict()
    hltb_scores = dict()
    base_scores = {'metacritics-critics': 100, 'metacritics-users': 10, 'steam-positive': 100, 
                'backloggd-rating': 5, 'igdb-rating': 100, 'moby-internal-score': 10}

    for key, val in game_obj.items():
        if val in ['', '#'] or not val:
            continue

        if any(x in key for x in ['summary', 'description', 'intro', 'plot', 'story', 'gameplay', 'synopsis', 'reception']):
            if 'riot' not in key and len(val) > 50:
                new_obj['sites'].add(key.split('-')[0].title())

        if key in ['metacritics-critics', 'metacritics-users', 'steam-positive', 
            'backloggd-rating', 'igdb-rating', 'moby-internal-score']:
            try:
                scores[key.replace('-', ' ').title()] = [round(float(val), 1), get_score_color(float(val), base_scores[key])]
            except ValueError as _:
                pass
            continue

        if key in ['hltb-main', 'hltb-main+', 'hltb-complete']:
            hltb_scores[key.replace('-', ' ').title()] = [val, 'darkcyan']
            continue
        
        if key == 'steam-nb-users':
            scores['Steam #Users'] = [val, 'hotpink']

        if 'release-date' in key:
            release_date.append(val)
            continue
        
        if '-genres' in key and 'moby' not in key:
            genres.update(val.split('; '))
            continue

        '''
        if 'similar-titles' in key or 'similar_games' in key:
            for title in val.split('; '):
                if title in all_games:
                    similar_games.append(title)
            continue
        '''
        
    if len(genres) > 0:
        new_obj['Genres'] = list(genres)
    if len(similar_games) > 0:
        new_obj['Similar Games'] = similar_games
    if len(release_date) > 0:
        new_obj['Release Date'] = release_date
    new_obj['sites'] = sorted(new_obj['sites'])
    scores.update(hltb_scores)
    if len(scores) > 0:
        new_obj['score'] = scores
    return new_obj


def organise_game_frontend(game_obj):
    new_game_obj = {'title': game_obj['title']}
    base_scores = {'metacritics-critics': 100, 'metacritics-users': 10, 'steam-positive': 100, 
                'backloggd-rating': 5, 'igdb-rating': 100, 'moby-internal-score': 10, 'rawg-score': 5}
    
    # Scores
    available_scores = ['backloggd-rating','igdb-rating', 'metacritics-critics', 
              'metacritics-users', 'moby-internal-score', 'steam-positive', 'rawg-score']
    scores = dict()
    for key in available_scores:
        if key in game_obj:
            try:
                val = game_obj[key]
                val = float(val)
                if val > 0:
                    scores[key.replace('-', ' ').title()] = [round(val, 1), get_score_color(val, base_scores[key])]
            except ValueError as _:
                pass
            continue

    if 'steam-nb-users' in game_obj:
        val = game_obj['steam-nb-users']
        if val not in ['', '#', '0', '/']:
            scores['Steam #Users'] = [val, 'hotpink']

    if 'steam-all-time-peaks' in game_obj:
        val = game_obj['steam-all-time-peaks']
        if val not in ['', '#', '0', '/']:
            scores['Steam Peak #Users'] = [val, 'hotpink']
    
    for key in ['hltb-main', 'hltb-main+', 'hltb-complete']:
        if key in game_obj:
            val = game_obj[key]
            if val not in ['', '#', '0', '/', '0.0', 0.0]:
                scores[key.replace('-', ' ').title()] = [val, 'darkcyan']
        continue

    if len(scores) > 0:
        new_game_obj['scores'] = scores

    # Genres
    key = 'Genres'
    if key in game_obj and len(game_obj[key]) > 0:
        new_game_obj[key] = game_obj[key]
    
    key = 'Release Date'
    if key in game_obj and len(game_obj[key]) > 0:
        new_game_obj[key] = game_obj[key][0] if game_obj[key][0] != '' else game_obj[key][1]

    key = 'rawg-achievements'
    if key in game_obj and len(game_obj[key]) > 0:
        new_game_obj['RAWG Achievements'] = game_obj[key]

    key = 'psnprofiles-achievements'
    if key in game_obj and len(game_obj[key]) > 0:
        new_game_obj['Trophies'] = game_obj[key]

    key = 'steam-achievements'
    if key in game_obj and len(game_obj[key]) > 0:
        new_game_obj['Steam Achievements'] = game_obj[key]

    new_game_obj['sites'] = set()
    for key in ['backloggd-description', 'gamesdb-description', 'giantbomb-intro', 'giantbomb-description', 
                'giantbomb-raw', 'igdb-storyline', 'igdb-summary', 'metacritics-description', 'moby-description',
                'moby-raw', 'rawg-description', 'steam-description', 'steam-summary', 'steam-raw',
                'wikipedia-summary', 'wikipedia-gameplay', 'wikipedia-plot', 'wikipedia-synopsis', 'wikipedia-reception',
                'wikipedia-raw']:
        val = game_obj.get(key, '')
        if len(val) > 50:
            new_game_obj[key] = val
            new_game_obj['sites'].add(key.split('-')[0].title())
    new_game_obj['sites'] = sorted(new_game_obj['sites'])

    cover = 'Covers New/' + game_obj['path'] + ' Cover.jpg'
    if not os.path.exists('static/' + cover):
        cover = 'Covers New/blank Cover.jpg'
    new_game_obj['cover'] = cover

    ch = game_obj['title'][0].upper()
    if ch not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        ch = '#'
    image_list = []
    for ind in range(1, 21):
        img_path = 'Temp/' + ch + '/' + game_obj['path'] + ' ' + str(ind) + '.jpg'
        if os.path.exists('static/' + img_path):
            image_list.append(img_path)
    new_game_obj['gallery'] = image_list

    if 'backloggd-split-rating' in game_obj:
        new_rating_dict = dict()
        for rating, rating_count in game_obj['backloggd-split-rating'].items():
            try:
                int_count = int(rating_count)
                new_rating_dict[rating] = int_count
            except Exception as _:
                    new_rating_dict[rating] = 0
        new_game_obj['backloggd-split-rating'] = new_rating_dict

    similar_games = []
    if 'Similar Games' in game_obj:
        for sim in game_obj['Similar Games']:
            sim_game = get_mongo_collection().find_one({'title': sim}, {'title': 1, 'path': 1, '_id': 0})
            if sim_game:
                similar_games.append(sim_game)
        new_game_obj['similar_games'] = similar_games
    
    # Read raw pages and decompress them
    if 'giantbomb-raw' in game_obj:
        new_game_obj['giantbomb-raw'] = zlib.decompress(game_obj['giantbomb-raw']).decode('utf-8')
    if 'moby-raw' in game_obj:
        new_game_obj['moby-raw'] = zlib.decompress(game_obj['moby-raw']).decode('utf-8')
    if 'steam-raw' in game_obj:
        new_game_obj['steam-raw'] = zlib.decompress(game_obj['steam-raw']).decode('utf-8')
    if 'wikipedia-raw' in game_obj:
        new_game_obj['wikipedia-raw'] = zlib.decompress(game_obj['wikipedia-raw']).decode('utf-8')
    # if 'rawg-raw' in game_obj:
    #     new_game_obj['rawg-raw'] = zlib.decompress(game_obj['rawg-raw']).decode('utf-8')

    for key in ['backloggd-url', 'gamesdb-url', 'metacritics-url', 'moby-url', 'rawg-url', 'steam-url', 'wikipedia-url']:
        if key in game_obj:
            new_game_obj[key] = game_obj[key]
    return new_game_obj
