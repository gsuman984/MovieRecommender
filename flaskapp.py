from flask import Flask, render_template, request, redirect
import pickle 
import requests
import random

# unpickling movies dataframe and similarities array
movies = pickle.load(open("movies.pkl", 'rb'))
similarities = pickle.load(open("similarities.pkl", 'rb'))
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
    suggest_count = 10
    L = same_series[:suggest_count]
    suggest_count -= len(L)
    if not suggest_count: return L
    # for s in all_suggest:
    #     if not same_series or not suggest_count: break
    #     if s[0] in same_series:
    #         L.append(s[0])
    #         same_series.remove(s[0])
    #         suggest_count -= 1
    for s in all_suggest[1:]:
        if not suggest_count: break
        if s[0] not in L: 
            L.append(s[0])
            suggest_count -= 1
    reco = movies[['id', 'title', 'title_year']].iloc[L]
    reco['posters'] = reco['id'].apply(fetch_poster)
    return list(reco['title']), list(reco['title_year']), list(reco['posters'])


########################################################################
app = Flask(__name__)

@app.route('/')
def home():
    indices = [i for i in range(30)]
    random.shuffle(indices)
    popular_movies = movies.iloc[indices[:12]]
    posters = popular_movies['id'].apply(fetch_poster)
    popular_movies = list(zip(popular_movies['title'],popular_movies['title_year'], posters))
    return render_template('home.html',allmovies=movies['title'],popular_movies=popular_movies)

@app.route('/recommendations',methods=['GET','POST'])
def recommendations():
    # pass
    if request.method == 'POST':
        requested_movie = request.form.get('movie_name')
        return redirect(f'/recommendations-{requested_movie}')
    return render_template('recommend.html',allmovies=movies['title'], requested_movie=None, recommended_movies=None)


@app.route('/recommendations-<movie>', methods=['GET','POST'])
def recommend_movie(movie):
    requested_movie = movie
    recommends = None
    try:
        title,title_year,poster = recommend(movie)
        recommends = list(zip(title, title_year, poster))
        movie_index = movies[movies['title']==movie].index[0]
        requested_movie_title = movies['title'][movie_index]
        requested_movie_titleyear = movies['title_year'][movie_index]
        requested_movie_poster = fetch_poster(movies['id'][movie_index])
        requested_movie = (requested_movie_title, requested_movie_titleyear, requested_movie_poster)
        return render_template('recommend.html',allmovies=movies['title'], requested_movie=requested_movie, recommended_movies = recommends)
        pass 
    except Exception:
        return redirect('/')
        pass

app.run(debug=True)