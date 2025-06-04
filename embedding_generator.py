import json
import torch
import pickle
import torch.nn as nn
from tqdm.notebook import tqdm
from sentence_transformers import SentenceTransformer, util

text_model = SentenceTransformer('all-MiniLM-L6-v2')
device = "cuda" if torch.cuda.is_available() else "cpu"
projection_layer_image = nn.Linear(512, 384).to(device)

def encode_text(text):
    return text_model.encode(text, convert_to_tensor=True)


def retrieve_similar_documents(query, embeddings, num_similar=20):
    if isinstance(query, str):  # Query is a text
        query_embedding = encode_text(query)
    else:
        raise ValueError("Query should be either text or image.")

    similarities = util.pytorch_cos_sim(query_embedding, embeddings)
    
    # Get top similar document indices
    top_results = torch.topk(similarities, num_similar)
    
    return top_results


if __name__ == '__main__':

    with open('games_text.json', 'r') as file:
        games_text = json.load(file)

    games_embedding = dict()
    for game_title, game in games_text.items():
        game_text = '[' + game_title + ']:\n\n' \
            + '\n\n'.join([game[key] for key in game.keys()])
        games_embedding[game_title] = dict()
        games_embedding[game_title]['text'] = game_text
        games_embedding[game_title]['embedding'] = encode_text(game_text)
        
    with open('all_text_emb.pkl', 'wb') as file:
        pickle.dump(games_embedding, file)
