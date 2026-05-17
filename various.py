import json
import time
import pymongo


myclient = pymongo.MongoClient('mongodb://localhost:27017/')
mycol = myclient['local']['MyGames']

from crawlers.psnprofiles import PSNProfilesCrawler
psn_crawler = PSNProfilesCrawler()

new_games_dict = dict()
all_games = list(mycol.find({}, {'_id': 0, 'title': 1, 'rawg-achievements': 1}))

count = 0
for game in all_games:
    
    new_title = game['title'].replace('#', '%23').replace(' (Retro)', '')
    if new_title == 'Resident Evil 4 Remake':
        psn_helper = {'psnprofiles-title': 'Resident Evil 4', 'psnprofiles-score': 1.0, 'psnprofiles-success': True,
                      'psnprofiles-url': 'https://psnprofiles.com/trophies/21540-resident-evil-4'}
    else:
        psn_helper = psn_crawler.get_url(new_title, 0)
    psn_info = psn_crawler.get_info(psn_helper['psnprofiles-url'], psn_helper['psnprofiles-score'])
    
    if len(psn_info.get('psnprofiles-achievements', [])) > 0:
        new_games_dict[game['title']] = {'title': game['title']}
        new_games_dict[game['title']].update(psn_helper)
        new_games_dict[game['title']].update(psn_info)
        time.sleep(1)
        
    count += 1
    print(game['title'], psn_info['psnprofiles-success'], 
          len(psn_info.get('psnprofiles-achievements', [])),
          len(game.get('rawg-achievements', [])))
    

with open('psn.json', 'w', encoding='utf-8') as file:
    json.dump(new_games_dict, file)
