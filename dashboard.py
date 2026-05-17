import numpy as np
import pandas as pd
from util.utility import get_mongo_collection

import streamlit as st
import plotly.express as px


all_games = list(get_mongo_collection().find({}, {'_id': 0, 'metacritics-critics': 1, 'metacritics-users': 1, 'platform': 1, 'Top Genres': 1,
                                             'steam-positive': 1, 'steam-nb-users': 1, 'hltb-main': 1, 'giantbomb-franchises': 1,
                                             'hltb-main+': 1, 'hltb-complete': 1, 'Release Date': 1, 'title': 1, 'Retro': 1}))


def normalize_release_date(date_str_list):
    ''' Normalize release date to a standard format (YYYY-MM-DD). '''

    temp_date = '1980-01-01'
    for date_str in date_str_list:
        if date_str != '':
            temp_date = date_str
            break
    return pd.to_datetime(temp_date).to_pydatetime()


@st.cache_data
def get_tabular_data():
    games_list = []
    for game_obj in sorted(all_games, key=lambda x: x['title'].lower()):
        games_list.append(
            [game_obj['title'],
            normalize_release_date(game_obj.get('Release Date', [])), game_obj.get('platform', '/'),
            game_obj.get('metacritics-critics', np.nan),
            game_obj.get('metacritics-users', np.nan),
            game_obj.get('steam-positive', np.nan),
            game_obj.get('steam-nb-users', np.nan),
            game_obj.get('hltb-main', np.nan),
            game_obj.get('hltb-main+', np.nan),
            game_obj.get('hltb-complete', np.nan),
            game_obj.get('Top Genres', [])]
        )
    
    games_df =  pd.DataFrame(games_list, columns = ['Title', 'Release Date', 'Platform', 'Metacritics Critics',
                                               'Metacritics Users', 'Steam Positive', 'Steam Nb Users',
                                               'HLTB Main', 'HLTB Main+', 'HLTB Complete', 'Genres'])
    games_df['Release Date'] = pd.to_datetime(games_df['Release Date'], errors='coerce')
    return games_df

# -----------------------------
# 1. Generate or Load Data
# -----------------------------
games = get_tabular_data()

# -----------------------------
# 2. Dashboard Layout
# -----------------------------
st.set_page_config(page_title='My Games Dashboard', layout='wide')
st.title('🎓 My Games Dashboard')

# Display info in a Streamlit-friendly way
st.write("Dataset loaded:")
st.write(games.shape)   # number of rows/columns
  # preview first rows

# Filters
with st.sidebar:
    st.header('🔍 Filters')
    min_date = games['Release Date'].min().to_pydatetime()
    max_date = games['Release Date'].max().to_pydatetime()  
    date_range = st.slider('Release Date Range', min_date, max_date, value=(min_date, max_date))
    games_filtered = games[(games['Release Date'] >= date_range[0]) & (games['Release Date'] <= date_range[1])]
    
    # Filter game platform
    platforms = sorted(games['Platform'].unique().tolist())
    selected_platforms = st.multiselect('Select Platforms', platforms, default=platforms)
    games_filtered = games_filtered[games_filtered['Platform'].isin(selected_platforms)]

    # Filter genres
    all_genres = set()
    for genres_list in games['Genres']:
        for genre in genres_list:
            all_genres.add(genre)
    all_genres = sorted(all_genres)
    selected_genres = st.multiselect('Select Genres', all_genres, default=all_genres)
    if selected_genres:
        games_filtered = games_filtered[games_filtered['Genres'].apply(lambda genres: any(genre in genres for genre in selected_genres))]

    st.write(f'Total Games Displayed: {len(games_filtered)}')

col1, col2 = st.columns(2)

with col1:
    platform_counts = games_filtered['Platform'].value_counts().reset_index()
    platform_counts.columns = ['Platform', 'Count']

    fig = px.pie(
        platform_counts,
        values='Count',
        names='Platform',
        title='🎮 Platform Distribution',
        hole=0.3  # optional, makes it a donut chart
    )

    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    genres_counts = games_filtered['Genres'].explode().value_counts().reset_index()
    genres_counts.columns = ['Genres', 'Count']

    fig = px.pie(
        genres_counts,
        values='Count',
        names='Genres',
        title='🎮 Genre Distribution',
        hole=0.3  # optional, makes it a donut chart
    )

    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

st.dataframe(games_filtered)
