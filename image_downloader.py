import json
import time
import random
import string
import requests


nb_images = 10
nb_artworks = 5
alphabet = list(string.ascii_uppercase)


def get_images(game_obj):
    image_nb = 1
    images_count = 1
    folder = game_obj['title'][0][0].upper()
    if folder not in alphabet:
        folder = '#'
    image_list = []
    
    images_path = 'Pictures 2/' + folder + '/' + game_obj['title'] + '_'
    images_path = images_path.replace(':', ' -')
    # images_path = 'Pictures/Test/' + game_obj['title'] + '_'
    image_list.extend(game_obj.get('steam-images', []))
    image_list.extend(game_obj.get('igdb-screenshots', []))
    image_list.extend(game_obj.get('riot-screenshots', []))
    image_list.extend(game_obj.get('giantbomb-screenshots', []))

    for sc_src in random.sample(image_list, min(nb_images, len(image_list))):
        try:
            response = requests.get(sc_src)
            with open(images_path + str(image_nb) + '.jpg', 'wb') as img_file:
                    img_file.write(response.content)
            image_nb += 1
            images_count += 1
        except Exception as _:
            continue

    image_nb = 1
    artworks = game_obj.get('igdb-artworks', [])
    for sc_src in random.sample(artworks, min(nb_artworks, len(artworks))):
        try:
            response = requests.get(sc_src)
            with open(images_path + str(image_nb) + '_ART.jpg', 'wb') as img_file:
                    img_file.write(response.content)
            image_nb += 1
            images_count += 1
        except Exception as _:
            continue
    
    if 'igdb-cover' in game_obj:
        try:
            response = requests.get(game_obj['igdb-cover'])
            with open(images_path + 'Cover.jpg', 'wb') as img_file:
                img_file.write(response.content)
        except Exception as _:
            pass
    
    return images_count, images_path


def get_gamesdb_images():

    with open('ordered_ultimate_games.json', 'r', encoding='utf-8') as file:
        retro = json.load(file)
    for game_title, game in retro.items():
        count = 1
        if 'gamesdb-images' in game:
            try:
                for _, img_list in game['gamesdb-images'].items():
                    if 'Fanart - Background' in img_list[0] or 'Banner' in img_list[0] or 'Arcade' in img_list[0]:
                        for img in img_list[1:]:
                            response = requests.get(img)
                            images_path = 'Fanart/' + game_title + ' _' + str(count) + '.jpg'
                            with open(images_path.replace(':', ' -'), 'wb') as img_file:
                                img_file.write(response.content)
                                count += 1
            except Exception as e:
                print(game_title, 'Error', e)
        if 'gamesdb-alternative-images' in game:
            try:
                for _, img_list in game['gamesdb-alternative-images'].items():
                    if 'Fanart - Background' in img_list[0] or 'Banner' in img_list[0] or 'Arcade' in img_list[0]:
                        for img in img_list[1:]:
                            response = requests.get(img)
                            images_path = 'Fanart/' + game_title + ' _' + str(count) + '.jpg'
                            with open(images_path.replace(':', ' -'), 'wb') as img_file:
                                img_file.write(response.content)
                                count += 1
            except Exception as e:
                print(game_title, 'Error', e)
        print(game_title)
        time.sleep(2)

if __name__ == '__main__':
     
    '''
    with open('ultimate_games.json', 'r', encoding='utf-8') as file:
        ultimate_games = json.load(file)

    for ind, game in enumerate(ultimate_games.values()):
        images_count, images_path = get_images(game)
        game['image_path'] = images_path
        game['images_count'] = images_count
        print(ind, game['title'], '#', images_count, '#', images_path)
    
    with open('ultimate_games.json', 'w', encoding='utf-8') as file:
        json.dump(ultimate_games, file)
    '''
    get_gamesdb_images()
