import json
from bisect import bisect_left

from util.utility import get_mongo_collection, get_similar_games
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


# Loading embeddings (local model) and Chroma DB
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = Chroma(
    persist_directory="./chroma_vg_db",
    embedding_function=embeddings
)


if __name__ == '__main__':

    my_col = get_mongo_collection()

    games_titles = set(my_col.distinct('titles'))

    with open('new_games_2.json', 'r', encoding='utf-8') as file:
        new_games = json.load(file).keys()

    for game in new_games:
        game_obj = my_col.find_one({'title': game}, {'title': 1, 'similar_games_sites': 1, '_id': 1})

        similar_games_ai, scores_ai = get_similar_games(game, db, top_k=40)[:20]

        for ind, sim_game in enumerate(similar_games_ai):
            sim_game_obj = my_col.find_one({'title': sim_game}, {'title': 1, 
                                                                 'similar_games_sites': 1, 
                                                                 'similar_games_ai': 1, 
                                                                 'similar_games_ai_scores': 1, '_id': 1})
            
            order_ind = bisect_left(sim_game_obj['similar_games_ai_scores'], scores_ai[ind])
            sim_game_obj['similar_games_ai'].insert(order_ind, sim_game)
            sim_game_obj['similar_games_ai_scores'].insert(order_ind, scores_ai[ind])

            sim_game_obj['similar_games_ai'] = sim_game_obj['similar_games_ai'][:-1]
            sim_game_obj['similar_games_ai_scores'] = sim_game_obj['similar_games_ai_scores'][:-1]

            sim_accepted_games = sim_game_obj['similar_games_ai'][:8] + sim_game_obj['similar_games_sites'][:10 - min(8, len(sim_game_obj['similar_games_ai']))]
            my_col.update_one({'title': sim_game}, {'$set': {'Similar Games': sim_accepted_games}})

        accepted_games = similar_games_ai[:8] + game_obj['similar_games_sites'][:10 - min(8, len(similar_games_ai))]
        my_col.update_one({'title': game}, {'$set': {'Similar Games': accepted_games, 
                                                     'similar_games_ai': similar_games_ai,
                                                     'similar_games_ai_scores': scores_ai}})
