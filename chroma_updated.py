import json
from util.utility import get_mongo_collection, generate_text
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


# Loading embeddings (local model) and Chroma DB
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = Chroma(
    persist_directory="./chroma_vg_db",
    embedding_function=embeddings
)


if __name__ == '__main__':

    with open('new_games_2.json', 'r', encoding='utf-8') as file:
        new_games = list(json.load(file).keys())

    games_text = []
    texts = []
    metadatas = []

    for game in list(get_mongo_collection().find({'title': {'$in': new_games}})):
        title = game.get('title', '#')
        games_text =  generate_text(game)

        for source, text in games_text.items():
            texts.append(text)
            metadatas.append({
                "game": title,
                "source": source
            })

        for key in ['giantbomb-franchises', 'giantbomb-platforms', 'giantbomb-themes', 'igdb-game_engines', 'igdb-keywords',
                    'igdb-player_perspectives', 'igdb-themes', 'moby-aliases', 'moby-genres', 'moby-reviews',
                    'moby-tags', 'steam-tags', 'wikipedia-genre', 'giantbomb-developers', 'giantbomb-genres', 'giantbomb-publishers',
                    'igdb-genres', 'steam-developers', 'steam-genres', 'franchise']:
            
            value = game.get(key, None)
            if isinstance(value, str):
                # simple key-value text
                texts.append(value)
                metadatas.append({"source": key, "game": title})

            elif value and key == 'moby-genres':
                moby_genres = ''
                for subkey, subvalue in value.items():
                    moby_genres += subkey + ': ' + subvalue + ' / '
                texts.append(moby_genres)
                metadatas.append({"source": "moby-genres", "game": title})

            elif isinstance(value, dict):
                # nested dict like moby-genres or moby-reviews
                for subkey, subvalue in value.items():
                    if isinstance(subvalue, str):
                        texts.append(subvalue)
                        metadatas.append({"source": f"{key}.{subkey}", "game": title})
                    elif isinstance(subvalue, list):
                        for item in subvalue:
                            # handle list of dicts (like reviews)
                            text_piece = item.get("review") or str(item)
                            texts.append(text_piece)
                            # keep numeric values like score in metadata
                            md = {"source": f"{key}.{subkey}", "game": title}
                            metadatas.append(md)

    # Add new games to the DB as needed
    BATCH_SIZE = 500

    print('Adding games to ChromaDB ...')
    for i in range(0, len(texts), BATCH_SIZE):
        batch_texts = texts[i:i + BATCH_SIZE]
        batch_metadatas = metadatas[i:i + BATCH_SIZE]

        db.add_texts(texts=batch_texts, metadatas=batch_metadatas)
    print('Finished updating ChromaDB ...')
