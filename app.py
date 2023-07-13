import pandas as pd
import pickle
import streamlit as st 
import requests

# unpickling movies dataframe and similarities array
movies = pickle.load(open("movies.pkl", 'rb'))
similarities = pickle.load(open("similarities.pkl", 'rb'))
# st.write(similarities.dtype)
# movie search engline
def movie_search_engine(movie_name):
    L = []
    for i in range(len(movies['title'])):
        name = movies['title'][i]
        if movie_name.lower() in name.lower():
            L.append(i)
    return movies.iloc[L]

# form same series/collections
def from_same_series(movie_index):
    series = movies['belongs_to_collection'][movie_index]
    L = []
    for i in range(movies.shape[0]):
        if i != movie_index and series != [''] and series == movies['belongs_to_collection'][i]:
            L.append(i)
    return L


# fetch poster url
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=5e5a3db9c6aa54131b8e8522654639d4"
    response = requests.get(url).json()
    return "https://image.tmdb.org/t/p/w500" + response['poster_path']


# recommending function
def recommend(movie):
    movie_index = movies[movies['title']==movie].index[0]
    all_suggest = sorted(enumerate(similarities[movie_index]), reverse=True, key=lambda x : x[1])
    same_series = from_same_series(movie_index)
    L = []
    suggest_count = 10
    for s in all_suggest:
        if not same_series or not suggest_count: break
        if s[0] in same_series:
            L.append(s[0])
            same_series.remove(s[0])
            suggest_count -= 1
    for s in all_suggest[1:]:
        if not suggest_count: break
        if s[0] not in L: 
            L.append(s[0])
            suggest_count -= 1
    reco = movies[['id', 'title']].iloc[L]
    reco['posters'] = reco['id'].apply(fetch_poster)
    return list(reco['posters']), list(reco['title'])



st.title("Movie Reccomender System")
selected = st.selectbox("Enter Movie Name : ", movies['title'], help="List of 10 most similar movies will be recommended!")
if st.button("Recommend"):
    st.info("Your Selected Movie : ", icon='📌')
    movie_index = movies[movies['title']==selected].index[0]
    st.image(fetch_poster(movies['id'][movie_index]), width=120)
    st.write(selected)
    poster_links, titles = recommend(selected)
    st.info("Recommended Movies For You : ", icon='📌')
    col = st.columns(5)
    for i in range(len(poster_links)):
        col[i%5].image(poster_links[i], width=120, caption=titles[i])
