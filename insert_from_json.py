import json
import zlib
import pymongo


if __name__ == "__main__":
    myclient = pymongo.MongoClient('mongodb://localhost:27017/')
    mycol = myclient['local']['MyGames']

    all_games_titles = {v['title'] for v in mycol.find({}, {'_id': 0, 'title': 1})}

    with open('new_games_2.json', 'r', encoding='utf-8') as file:
        new_games = json.load(file)

    for game in new_games:
        if game in all_games_titles:
            print(game, 'already in database')

    with open ('Genres.txt', 'r', encoding='utf-8') as file:
        accepted_genres = file.readlines()

    genres_dict = dict()
    for line in accepted_genres:
        line = line.replace('\n', '')
        split_line = line.split('\t')
        orig_genre, genre_list = split_line[0], split_line[1].split(' # ')
        genres_dict[orig_genre] = genre_list

    for game, game_obj in new_games.items():
        new_genres = set()
        for genre in game_obj.get('Genres', []):
            if genre in genres_dict and genres_dict[genre][0] != '/':
                new_genres.update({g for g in genres_dict[genre]})
                
    
        game_obj['Top Genres'] = sorted(new_genres)

    for game, game_obj in new_games.items():
        similar_games = []
        for key, value in game_obj.items():
            if '-raw' in key:
                game_obj[key] =  zlib.compress(str(value).encode('utf8'))
        
            if 'similar-titles' in key or 'similar_games' in key:
                for title in value.split('; '):
                    if title in all_games_titles or title in new_games:
                        similar_games.append(title)
                continue

        if len(similar_games) > 0:
            game_obj['Similar Games'] = similar_games

        
        if game in all_games_titles:
            mycol.update_one({'title': game}, {'$set': game_obj})
        else:
            mycol.insert_one(game_obj)
      
    for game, game_obj in new_games.items():
        print(game, '#', game_obj.get('platform'), '#', game_obj.get('franchise', ''), '#',
            game_obj.get('Release Date', [None])[0], '#',
            game_obj.get('metacritics-critics', '/'), '#',
            game_obj.get('metacritics-users', '/'), '#',
            game_obj.get('steam-positive', '/'), '#',
            game_obj.get('steam-nb-users', '/'), '#',
            game_obj.get('hltb-main', '/'), '#',
            game_obj.get('hltb-main+', '/'), '#',
            game_obj.get('hltb-complete', '/')
        )
