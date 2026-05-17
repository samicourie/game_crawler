import json
import time
from util.utility import get_mongo_collection, get_path, organise_game_data
from util.image_utility import ImageUtility
from crawlers.backloggd import BackloggdCrawler
from crawlers.gamesdb import GamesDBCrawler
from crawlers.giantbomb import GiantbombCrawler
from crawlers.hltb import HLTBCrawler
from crawlers.igdb import IGDBCrawler
from crawlers.meta import MetaCrawler
from crawlers.moby import MobyCrawler
from crawlers.psnprofiles import PSNProfilesCrawler
# from crawlers.rawg import RawgCrawler
from crawlers.rawg_2 import RawgCrawler
# from crawlers.riot import RiotCrawler
from crawlers.steam import SteamCrawler
from crawlers.wikipedia import WikipediaCrawler


def generate_text(game_obj):
    text_obj = dict()
    str_obj = ''
    if game_obj.get('steam-description', '#') != '#':
        str_obj += 'Description: ' + game_obj['steam-description'] + '\n'
    if game_obj.get('steam-summary', '#') != '#':
        str_obj += 'Summary: ' + game_obj['steam-summary'] + '\n'
    if game_obj.get('steam-tags', '#') != '#':
        str_obj += 'Tags: ' + game_obj['steam-tags'] + '\n'
    if game_obj.get('steam-genres', '#') != '#':
        str_obj += 'Genres: ' + game_obj['steam-genres'] + '\n'
    if str_obj != '':
        text_obj['text-steam'] = 'Steam: \n' + str_obj
    
    if game_obj.get('metacritics-description', '#') != '#':
        game_obj['text-metacritics'] = 'Metacritic: \n' + game_obj['metacritics-description']  + '\n'

    if game_obj.get('rawg-description', '#') != '#':
        game_obj['text-rawg'] = 'RAWG: \n' + game_obj['rawg-description']  + '\n'
    
    str_obj = ''
    if game_obj.get('wikipedia-summary', '#') != '#':
        str_obj += 'Summary: ' + game_obj['wikipedia-summary'] + '\n'
    if game_obj.get('wikipedia-gameplay', '#') != '#':
        str_obj += 'Gameplay: ' + game_obj['wikipedia-gameplay'] + '\n'
    if game_obj.get('wikipedia-plot', '#') != '#':
        str_obj += 'Plot: ' + game_obj['wikipedia-plot'] + '\n'
    if game_obj.get('wikipedia-synopsis', '#') != '#':
        str_obj += 'Synopsis: ' + game_obj['wikipedia-synopsis'] + '\n'
    if game_obj.get('wikipedia-genre', '#') != '#':
        str_obj += 'Genres: ' + game_obj['wikipedia-genre'] + '\n'
    if str_obj != '':
        text_obj['text-wikipedia'] = 'Wikipedia: \n' + str_obj

    str_obj = ''
    if game_obj.get('giantbomb-intro', '#') != '#':
        str_obj += 'Intro: ' + game_obj['giantbomb-intro'] + '\n'
    if game_obj.get('giantbomb-description', '#') != '#':
        str_obj += 'Description: ' + game_obj['giantbomb-description'] + '\n'
    if game_obj.get('giantbomb-genres', '#') != '#':
        str_obj += 'Genres: ' + game_obj['giantbomb-genres'] + '\n'
    if game_obj.get('giantbomb-themes', '#') != '#':
        str_obj += 'Themes: ' + game_obj['giantbomb-themes'] + '\n'
    if str_obj != '':
        text_obj['text-giantbomb'] = 'GiantBomb: \n' + str_obj

    str_obj = ''
    if game_obj.get('igdb-summary', '#') != '#':
        str_obj += 'Summary: ' + game_obj['giantbomb-summary'] + '\n'
    if game_obj.get('igdb-story', '#') != '#':
        str_obj += 'Story: ' + game_obj['igdb-story'] + '\n'
    if game_obj.get('igdb-keywords', '#') != '#':
        str_obj += 'Keywords: ' + game_obj['igdb-keywords'] + '\n'
    if game_obj.get('igdb-genres', '#') != '#':
        str_obj += 'genres: ' + game_obj['igdb-genres'] + '\n'
    if game_obj.get('igdb-themes', '#') != '#':
        str_obj += 'themes: ' + game_obj['igdb-themes'] + '\n'
    if game_obj.get('igdb-perspectives', '#') != '#':
        str_obj += 'Perspectives: ' + game_obj['igdb-perspectives'] + '\n'
    if str_obj != '':
        text_obj['text-igdb'] = 'IGDB: \n' + str_obj

    if game_obj.get('backloggd-description', '#') != '#':
        text_obj['text-backloggd'] = 'Backloggd: \n' + game_obj['backloggd-description']  + '\n'
    
    return text_obj


crawler_dict = {
    'backloggd': BackloggdCrawler(),
    'gamesdb': GamesDBCrawler(),
    # 'giantbomb': GiantbombCrawler(),
    'hltb': HLTBCrawler(),
    'igdb': IGDBCrawler(),
    'metacritics': MetaCrawler(),
    'moby': MobyCrawler(),
    'psnprofiles': PSNProfilesCrawler(),
    'rawg': RawgCrawler(),
    # 'riot': RiotCrawler(),
    'steam': SteamCrawler(),
    'wikipedia': WikipediaCrawler()
}


with open('new_games.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()


game_title = "Resident Evil Requiem"
"""
backloggd_helper = crawler_dict['backloggd'].get_url(game_title, 2026)
backloggd_info = crawler_dict['backloggd'].get_info(backloggd_helper['backloggd-url'], backloggd_helper['backloggd-score'])

gamesdb_helper = crawler_dict['gamesdb'].get_url(game_title, 2026)
gamesdb_info = crawler_dict['gamesdb'].get_info(gamesdb_helper['gamesdb-url'], gamesdb_helper['gamesdb-score'])

# giantbomb_info = crawler_dict['giantbomb'].get_api_info(game_title, 2023)

hltb_info = crawler_dict['hltb'].get_api_info(game_title, 2026)

igdb_helper = crawler_dict['igdb'].get_url(game_title, 2026)
igdb_info = crawler_dict['igdb'].get_info(igdb_helper['igdb-url'], igdb_helper['igdb-score'])

meta_helper = crawler_dict['metacritics'].get_url(game_title, 2026)
meta_info = crawler_dict['metacritics'].get_info(meta_helper['metacritics-url'], meta_helper['metacritics-score'])

moby_helper = crawler_dict['moby'].get_url(game_title, 2026)
moby_info = crawler_dict['moby'].get_info(moby_helper['moby-url'], moby_helper['moby-score'])

psn_helper = crawler_dict['psnprofiles'].get_url(game_title, 0)

psn_info = crawler_dict['psnprofiles'].get_info(psn_helper['psnprofiles-url'], 1, is_stored=False)

rawg_info = crawler_dict['rawg'].get_api_info(game_title, 2026)

# riot_helper = crawler_dict['riot'].get_url(game_title)
# riot_info = crawler_dict['riot'].get_info(riot_helper['riot-url'], riot_helper['riot-score'])

steam_helper = crawler_dict['steam'].get_url(game_title, 2026)
steam_info = crawler_dict['steam'].get_info(steam_helper['steam-url'], steam_helper['steam-score'])

wiki_helper = crawler_dict['wikipedia'].get_url(game_title)
wiki_info = crawler_dict['wikipedia'].get_info(wiki_helper['wikipedia-url'], wiki_helper['wikipedia-score'])
"""

my_game_col = get_mongo_collection()
all_games_paths = my_game_col.distinct('path')
all_games_titles = my_game_col.distinct('title')

with open ('Genres.txt', 'r', encoding='utf-8') as file:
    accepted_genres = file.readlines()

genres_dict = dict()
for line in accepted_genres:
    line = line.replace('\n', '')
    split_line = line.split('\t')
    orig_genre, genre_list = split_line[0], split_line[1].split(' # ')
    genres_dict[orig_genre] = genre_list

new_dict = dict()
count = 0
image_utility = ImageUtility()
for line in lines:
    line_arr = line.replace('\n', '').split('#')
    temp_line = line_arr[0].strip()
    temp_year = int(line_arr[1])
    temp_platform = line_arr[2].strip()
    
    str_obj = temp_line
    new_dict[temp_line] = {'title': temp_line, 'platform': temp_platform}
    if len(line_arr) > 3:
        temp_franchise = line_arr[3].strip()
        if temp_franchise not in [None, '']:
            new_dict[temp_line]['franchise'] = temp_franchise
    print(temp_line)
    # for site in crawler_dict:
    for site in crawler_dict:
        # print(temp_line, site)
        try:
            if site in ['hltb', 'giantbomb', 'rawg']:
                site_info = crawler_dict[site].get_api_info(temp_line, temp_year)
                new_dict[temp_line].update(site_info)
            else:
                site_helper = crawler_dict[site].get_url(temp_line, temp_year)
                if site_helper[site+'-success'] and site_helper[site+'-score'] >= crawler_dict[site].accepted_score:
                    site_info = crawler_dict[site].get_info(site_helper[site+'-url'], site_helper[site+'-score'])
                    new_dict[temp_line].update(site_helper)
                    new_dict[temp_line].update(site_info)
                else:
                    new_dict[temp_line].update({site+'-success': False})
            if site in ['giantbomb', 'metacritics']:
                time.sleep(5)
            elif site in ['psnprofiles']:
                time.sleep(3)
            else:
                time.sleep(1)
            str_obj += ' # ' + site + ':' + str(new_dict[temp_line].get(site+'-success', 'False'))
        except Exception as _:
            str_obj += ' # ' + site + ':' + str(new_dict[temp_line].get(site+'-success', 'False'))
        new_dict[temp_line].update({'giantbomb-success': False})
    
    new_dict[temp_line]['path'] = get_path(temp_line, all_games_paths)
    new_dict[temp_line].update(organise_game_data(new_dict[temp_line], all_games_titles, genres_dict))
    selected_images = image_utility.download_images(new_dict[temp_line])
    new_dict[temp_line]['selected_images'] = selected_images
    image_utility.reset()
    count += 1
    if count % 5 == 0:
        with open('new_games_2.json', 'w', encoding='utf-8') as file:
            json.dump(new_dict, file)
    print(str_obj)

with open('new_games_2.json', 'w', encoding='utf-8') as file:
    json.dump(new_dict, file)
