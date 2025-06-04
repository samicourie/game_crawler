import json
import time
from crawlers.backloggd import BackloggdCrawler
from crawlers.gamesdb import GamesDBCrawler
from crawlers.giantbomb import GiantbombCrawler
from crawlers.hltb import HLTBCrawler
from crawlers.igdb import IGDBCrawler
from crawlers.meta import MetaCrawler
from crawlers.moby import MobyCrawler
from crawlers.rawg import RawgCrawler
from crawlers.riot import RiotCrawler
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
    'giantbomb': GiantbombCrawler(),
    'hltb': HLTBCrawler(),
    'igdb': IGDBCrawler(),
    'metacritics': MetaCrawler(),
    'moby': MobyCrawler(),
    'rawg': RawgCrawler(),
    # 'riot': RiotCrawler(),
    'steam': SteamCrawler(),
    'wikipedia': WikipediaCrawler()}
"""
with open('new_games.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()
"""

with open('retro.json', 'r', encoding='utf-8') as file:
    retro_games = json.load(file)
"""

game_title = 'Hollow Knight'

backloggd_helper = crawler_dict['backloggd'].get_url(game_title)
backloggd_info = crawler_dict['backloggd'].get_info(backloggd_helper['backloggd-url'], backloggd_helper['backloggd-score'])

gamesdb_helper = crawler_dict['gamesdb'].get_url(game_title)
gamesdb_info = crawler_dict['gamesdb'].get_info(gamesdb_helper['gamesdb-url'], gamesdb_helper['gamesdb-score'])

giantbomb_info = crawler_dict['giantbomb'].get_api_info(game_title)

hltb_info = crawler_dict['hltb'].get_api_info(game_title)

igdb_helper = crawler_dict['igdb'].get_url(game_title)
igdb_info = crawler_dict['igdb'].get_info(igdb_helper['igdb-url'], igdb_helper['igdb-score'])

meta_helper = crawler_dict['metacritics'].get_url(game_title)
meta_info = crawler_dict['metacritics'].get_info(meta_helper['metacritics-url'], meta_helper['metacritics-score'])

moby_helper = crawler_dict['moby'].get_url(game_title)
moby_info = crawler_dict['moby'].get_info(moby_helper['moby-url'], moby_helper['moby-score'])

rawg_info = crawler_dict['rawg'].get_api_info(game_title)

riot_helper = crawler_dict['riot'].get_url(game_title)
riot_info = crawler_dict['riot'].get_info(riot_helper['riot-url'], riot_helper['riot-score'])

steam_helper = crawler_dict['steam'].get_url(game_title)
steam_info = crawler_dict['steam'].get_info(steam_helper['steam-url'], steam_helper['steam-score'])

wiki_helper = crawler_dict['wikipedia'].get_url(game_title)
wiki_info = crawler_dict['wikipedia'].get_info(wiki_helper['wikipedia-url'], wiki_helper['wikipedia-score'])
"""

wanted_crawlers = ['gamesdb']
new_dict = dict()
count = 0
for line in retro_games:
    temp_line = line.replace('\n', '')
    str_obj = temp_line
    new_dict[temp_line] = dict()
    for site in wanted_crawlers:
        # print(temp_line, site)
        try:
            if site in ['hltb', 'giantbomb', 'rawg']:
                site_info = crawler_dict[site].get_api_info(temp_line)
                new_dict[temp_line].update(site_info)
            else:
                site_helper = crawler_dict[site].get_url(temp_line)
                if site_helper[site+'-success'] and site_helper[site+'-score'] >= crawler_dict[site].accepted_score:
                    site_info = crawler_dict[site].get_info(site_helper[site+'-url'], site_helper[site+'-score'])
                    new_dict[temp_line].update(site_helper)
                    new_dict[temp_line].update(site_info)
                else:
                    new_dict[temp_line].update({site+'-success': False})
            if site in ['giantbomb', 'metacritics']:
                time.sleep(10)
            elif site in ['gamesdb']:
                time.sleep(5)
            else:
                time.sleep(1)
            str_obj += ' # ' + site + ':' + str(new_dict[temp_line].get(site+'-success', 'False'))
        except Exception as _:
            str_obj += ' # ' + site + ':' + str(new_dict[temp_line].get(site+'-success', 'False'))
    count += 1
    if count % 50 == 0:
        with open('gamesdb_retro.json', 'w', encoding='utf-8') as file:
            json.dump(new_dict, file)
    print(str_obj)

with open('gamesdb_retro.json', 'w', encoding='utf-8') as file:
    json.dump(new_dict, file)
