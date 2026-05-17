import os
import zlib
import json
import random
import string
from util.crawl_helper import CrawlHelper
from util.image_utility import ImageUtility
from util.utility import get_mongo_collection, organise_game_frontend, organise_game_data
from flask import Flask, render_template, jsonify, request, redirect, url_for

from langchain_chroma import Chroma
# from langchain_ollama import OllamaLLM
# from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings

app = Flask(__name__)


def search_chroma(query):
    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    db = Chroma(
        persist_directory='./chroma_vg_db',
        embedding_function=embeddings
    )

    source_filters = {'source': {'$in': ['steam-text', 'igdb-text', 'wikipedia-text', 'giantbomb-text', 'gamesdb-text',
                               'rawg-text', 'mobygames-text', 'backloggd-text', 'metacritic-text']}} 

    results = db.similarity_search(query, k=1000, filter=source_filters)
    best_by_game = []
    best_by_game_set = set()

    for doc in results:
        game = doc.metadata.get('game')
        if game not in best_by_game_set:
            best_by_game_set.add(game)
            best_by_game.append(game)

    res_size = 54
    # return top k unique games
    return best_by_game[:res_size]


@app.route('/')
def home():
    all_games = list(get_mongo_collection().find({}, {'title': 1, 'Intro': 1, 'path': 1, '_id': 0}))
    random_games = random.sample(all_games, 20)

    games_by_letter = {letter: [] for letter in string.ascii_uppercase}
    games_by_letter['#'] = []

    for game in random_games:
        ch = str(game)[0].upper()
        if ch in string.ascii_uppercase:
            games_by_letter[ch].append(game)
        else:
            games_by_letter['#'].append(game)

        cover = 'Covers New/' + game['path'] + ' Cover.jpg'
        if not os.path.exists('static/' + cover):
            cover = 'Covers New/blank Cover.jpg'
        game['cover'] = cover

    return render_template(
        'home.html',
        random_games=random_games,
        games_by_letter=games_by_letter
    )


@app.route('/media')
def media():
    games = list(get_mongo_collection().find({}, {'title': 1, 'Intro': 1, 'selected_images': 1,
                                                   'path': 1, '_id': 0}).sort('title', 1))

    game = games[0]
    cover = 'Covers New/' + game['path'] + ' Cover.jpg'
    if not os.path.exists('static/' + cover):
        cover = 'Covers New/blank Cover.jpg'
    game['cover'] = cover

    ch = game['title'][0].upper()
    if ch not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        ch = '#'
    image_list = []
    if 'selected_images' in game and len(game['selected_images']) > 0:
        image_list = game['selected_images']
    else:
        ch = game['title'][0].upper()
        if ch not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            ch = '#'
        for ind in range(1, 21):
            img_path = 'Temp/' + ch + '/' + game['path'] + ' ' + str(ind) + '.jpg'
            if os.path.exists('static/' + img_path):
                image_list.append(img_path)
    game['gallery'] = image_list

    return render_template(
        "media.html",
        games=games,
        game=game
    )


@app.route('/media/<game_title>')
def game_media(game_title):
    print(game_title)
    game = get_mongo_collection().find_one({'title': game_title}, {'title': 1, 'Intro': 1, 'selected_images': 1, 'path': 1, '_id': 0})
    cover = 'Covers New/' + game['path'] + ' Cover.jpg'
    if not os.path.exists('static/' + cover):
        cover = 'Covers New/blank Cover.jpg'
    game['cover'] = cover

    ch = game['title'][0].upper()
    if ch not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        ch = '#'
    image_list = []
    if 'selected_images' in game and len(game['selected_images']) > 0:
        image_list = game['selected_images']
    else:
        ch = game['title'][0].upper()
        if ch not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            ch = '#'
        for ind in range(1, 21):
            img_path = 'Temp/' + ch + '/' + game['path'] + ' ' + str(ind) + '.jpg'
            if os.path.exists('static/' + img_path):
                image_list.append(img_path)
    game['gallery'] = image_list

    if game:
        return jsonify(game)
    return jsonify({'error': 'not found'}), 404


@app.route('/game/<game_title>')
def game_detail(game_title):

    game = get_mongo_collection().find_one({'title': game_title})
    if not game:
        return 'Game not found', 404

    front_end_game = organise_game_frontend(game)
    return render_template('game_2.html', game=front_end_game)

@app.route('/crawl/<game_title>')
def crawl_game(game_title):

    game = get_mongo_collection().find_one({'title': game_title})
    if not game:
        return 'Game not found', 404

    front_end_game = organise_game_frontend(game)
    return render_template('crawl.html', game=front_end_game)

@app.route("/crawl", methods=["POST"])
def crawl():
    
    data = request.get_json()
    entries = data.get("entries", [])
    title = data.get('title', '')
    crawl_helper = CrawlHelper()
    results = {'title': title}
    results.update(crawl_helper.crawl_urls(entries))
    
    return jsonify(results)


@app.route('/edit/<game_title>', methods=["GET", "POST"])
def edit_document(game_title):
    temp_title = game_title
    if request.method == "POST":
        raw_json = request.form["json_data"]

        try:
            updated_doc = json.loads(json.loads(raw_json))
            temp_title = updated_doc.get('title', game_title)
            get_mongo_collection().update_one(
                {"title": game_title},
                {'$set': updated_doc}
            )
        except Exception as e:
            return f"Invalid JSON: {e}", 400

    game = get_mongo_collection().find_one({'title': temp_title}, 
                                           {'title': 1, 'platform': 1, 'franshise': 1, 'path': 1, '_id': 0,
                                            'Genres': 1, 'Release Date': 1, 'Top Genres': 1, 'new_title': 1,
                                            'Similar Games': 1, 'Developers': 1, 'Publishers': 1})
    front_end_game = organise_game_frontend(game)
    return render_template('edit.html', game=front_end_game, json_data=json.dumps(game, indent=2))


@app.route("/save_game_data", methods=["POST"])
def save_game_data():
    
    json_obj = request.get_json()
    data = json_obj['data']
    new_dict = dict()
    for key, val in data.items():
        if key == 'title':
            new_dict[key] = val
        else:
            new_dict.update(val)
    
    for key, val in new_dict.items():
        if key.endswith('-raw'):
            new_dict[key] = zlib.compress(str(val).encode('utf8'))
    
    
    # for key in list(data.keys()):
    game_obj = get_mongo_collection().find_one({'title': new_dict['title']})
    if json_obj['pictures_check'] or json_obj['cover_check']:
        image_util = ImageUtility()
        selected_images = image_util.download_images(game_obj=game_obj, download_images=json_obj['pictures_check'],
                                    download_cover=json_obj['cover_check'])
        new_dict['selected_images'] = selected_images
    game_obj.update(new_dict)
    all_games_titles = get_mongo_collection().distinct('title')

    ###############################################################################
    # To change: save genres dict in a more efficient way and not read from txt every time
    with open ('Genres.txt', 'r', encoding='utf-8') as file:
        accepted_genres = file.readlines()
    genres_dict = dict()
    for line in accepted_genres:
        line = line.replace('\n', '')
        split_line = line.split('\t')
        orig_genre, genre_list = split_line[0], split_line[1].split(' # ')
        genres_dict[orig_genre] = genre_list
    ###############################################################################
    game_obj.update(organise_game_data(game_obj, all_games_titles, genres_dict))
    get_mongo_collection().update_one({'title': game_obj['title']}, {'$set': game_obj})
    return jsonify({'success': True})


@app.route('/api/game-titles')
def game_titles():
    titles = list(get_mongo_collection().find({}, {'title': 1, '_id': 0}))
    titles = sorted([title['title'].replace('\n', '') for title in titles])
    return jsonify(titles)
    

@app.route('/api/games-by-letter')
def get_games_by_letter():
    letter = request.args.get('letter', '').upper()
    page = int(request.args.get('page', 1))
    page_size = 20

    skip = (page - 1) * page_size

    if letter == '#':
        query = { 'title': { '$regex': r'^[^A-Za-z]' } }
    else:
        query = { 'title': { '$regex': f'^{letter}', '$options': 'i' } }

    games = list(get_mongo_collection().find(query, {'title': 1, 'Intro': 1, 'path': 1, '_id': 0}).sort({'title': 1})
                 .skip(skip).limit(page_size+1))

    has_next = True
    if len(games) <= page_size:
        has_next = False
    games = games[:page_size]
    return jsonify({'games': games, 'has_next': has_next})


@app.route('/search', methods=['GET', 'POST'])
def search():
    per_page = 54
    page = int(request.args.get('page', 1))

    genres = get_mongo_collection().distinct('Top Genres')
    genres = set([v.strip() for v in genres if len(v) > 1])
    developers  = get_mongo_collection().distinct('Developers')
    developers  = set([v.strip() for v in developers if len(v) > 1])
    publishers  = get_mongo_collection().distinct('Publishers')
    publishers  = set([v.strip() for v in publishers if len(v) > 1])

    if request.method == 'POST':
        # build query params from form and redirect
        args = request.form.to_dict(flat=False)  # keeps multi-selects
        args['page'] = 1
        return redirect(url_for('search', **{k: v for k, vals in args.items() for v in (vals if isinstance(vals, list) else [vals])}))

    # GET: build query from request.args
    query = build_advance_search_query(request.args)
    
    # Backloggd dominant rating filter (Python)
    backloggd_star = request.args.get('backloggd')
    if backloggd_star:
        backloggd_res = get_mongo_collection().find({}, {'backloggd-split-rating': 1, '_id': 1})
        backloggd_ids = []
        for game in backloggd_res:
            split = game.get('backloggd-split-rating', {})
            if not split:
                continue
            # Convert counts to integers
            counts = {k: int(v) for k, v in split.items()}
            max_count = max(counts.values())
            # Keep game only if the chosen star has the max count
            if max_count > 5 and counts.get(str(backloggd_star)) == max_count:
                backloggd_ids.append(game['_id'])
        query['_id'] = {'$in': backloggd_ids}

    # Always run query (empty query = all games)
    total_results = get_mongo_collection().count_documents(query)
    total_pages = (total_results + per_page - 1) // per_page

    skip = (page - 1) * per_page

    # Fetch results (limit 50)
    if query:
        results = list(
            get_mongo_collection().find(query, {'title': 1, 'path': 1, 'Release Date': 1, 
                                                'igdb-summary': 1}).skip(skip).limit(per_page)
        )
    else:
        total_pages = 1
        results = list(get_mongo_collection().aggregate([{'$sample': {'size': per_page}}]))

    for game in results:
        cover = 'Covers New/' + game['path'] + ' Cover.jpg'
        if not os.path.exists('static/' + cover):
            cover = 'Covers New/blank Cover.jpg'
        game['cover'] = cover
        
    genres = sorted(genres)
    developers = sorted(developers)
    publishers = sorted(publishers)

    # Copy args for pagination links
    args = request.args.to_dict(flat=False)
    args.pop('page', None)  # remove page, we'll override it

    return render_template('search.html',
                           genres=genres,
                           developers=developers,
                           publishers=publishers,
                           results=results,
                           page=page,
                           total_pages=total_pages,
                           current_args=args)


def build_advance_search_query(form):
    query = {}

    # Title
    title = form.get('title')
    if title:
        query['title'] = {'$regex': title, '$options': 'i'}

    # Genres
    genres_selected = form.getlist('genres')
    if genres_selected:
        query['Top Genres'] = {'$in': genres_selected}

    # Developers
    devs_entry = form.get('developers')
    if devs_entry:
        query['Developers'] = {'$regex': devs_entry, '$options': 'i'}

    # Publishers
    pubs_entry = form.get('publishers')
    if pubs_entry:
        query['Publishers'] = {'$regex': pubs_entry, '$options': 'i'}

    # Platform
    platform = form.get('platform')
    if platform:
        query['platform'] = platform

    # Release date
    start = form.get('release_start')
    end = form.get('release_end')
    if start or end:
        release_range = {}
        if start:
            release_range['$gte'] = start
        if end:
            release_range['$lte'] = end
        query['Release Date.0'] = release_range

    # Score (normalize to 0–1 scale)
    score_input = form.get('score_min')
    if score_input:
        try:
            score_val = float(score_input) / 100.0
            query['$or'] = [
                {'score.Backloggd Rating.0': {'$gte': score_val * 5}},  # out of 5
                {'score.Igdb Rating.0': {'$gte': score_val * 100}},     # out of 100
                {'score.Metacritics Critics.0': {'$gte': score_val * 100}},
                {'score.Metacritics Users.0': {'$gte': score_val * 10}},
                {'score.Moby Internal Score.0': {'$gte': score_val * 10}},
                {'score.Steam Positive.0': {'$gte': score_val * 100}},
            ]
        except:
            pass

     # Score (normalize to 0–1 scale)
    score_input = form.get('score_max')
    if score_input:
        try:
            score_val = float(score_input) / 100.0
            query['$or'] = [
                {'score.Backloggd Rating.0': {'$lte': score_val * 5}},  # out of 5
                {'score.Igdb Rating.0': {'$lte': score_val * 100}},     # out of 100
                {'score.Metacritics Critics.0': {'$lte': score_val * 100}},
                {'score.Metacritics Users.0': {'$lte': score_val * 10}},
                {'score.Moby Internal Score.0': {'$lte': score_val * 10}},
                {'score.Steam Positive.0': {'$lte': score_val * 100}},
            ]
        except:
            pass

    # HLTB (playtime) filter
    hltb_mode = form.get('hltb_mode')
    hltb_hours = form.get('hltb_hours')
    if hltb_hours:
        try:
            hours = float(hltb_hours)
            condition = {'$lte': hours} if hltb_mode == 'less' else {'$gte': hours}
            query['$or'] = [
                {'score.Hltb Main.0': condition},
                {'score.Hltb Main+.0': condition},
                {'score.Hltb Complete.0': condition},
            ]
        except:
            pass

    return query


@app.route('/search_ai', methods=['GET', 'POST'])
def search_ai():
    text = ''
    results = []
    if request.method == 'POST':
        text = request.form.get('text', '')
        search_results = search_chroma(text)

        results = []
        for game in search_results:
            game_obj = get_mongo_collection().find_one({'title': game}, {'title': 1, 'path': 1, 'Release Date': 1, 'igdb-summary': 1})
            results.append(game_obj)

        for game in results:
            cover = 'Covers New/' + game['path'] + ' Cover.jpg'
            if not os.path.exists('static/' + cover):
                cover = 'Covers New/blank Cover.jpg'
            game['cover'] = cover

        order_map = {name: i for i, name in enumerate(search_results)}
        results.sort(key=lambda d: order_map.get(d['title'], len(search_results)))
    
    # Copy args for pagination links
    args = request.args.to_dict(flat=False)
    args.pop('page', None)  # remove page, we'll override it

    return render_template('search_ai.html', text=text, results=results, current_args=args)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
