import requests
import os

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# --- Populares ---
def get_popular_movies(limit=50):
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page=1"
    res = requests.get(url).json()
    return res.get("results", [])[:limit]

def get_popular_series(limit=50):
    url = f"https://api.themoviedb.org/3/tv/popular?api_key={TMDB_API_KEY}&language=en-US&page=1"
    res = requests.get(url).json()
    return res.get("results", [])[:limit]

# --- Detalhes individuais ---
def get_movie_details(movie_id: int):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    res = requests.get(url).json()
    return res

def get_series_details(series_id: int):
    url = f"https://api.themoviedb.org/3/tv/{series_id}?api_key={TMDB_API_KEY}&language=en-US"
    res = requests.get(url).json()
    return res

def get_movie_credits(movie_id: int):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={TMDB_API_KEY}&language=pt-BR"
    response = requests.get(url).json()
    return response

def get_series_credits(series_id: int):
    url = f"https://api.themoviedb.org/3/tv/{series_id}/credits?api_key={TMDB_API_KEY}&language=pt-BR"
    response = requests.get(url).json()
    return response

# --- Busca por nome ---
def search_movie(query: str, limit=30):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&language=en-US&query={query}&page=1"
    res = requests.get(url).json()
    results = res.get("results", [])
    results.sort(key=lambda x: x.get("popularity", 0), reverse=True)
    return results[:limit]

def search_series(query: str, limit=30):
    url = f"https://api.themoviedb.org/3/search/tv?api_key={TMDB_API_KEY}&language=en-US&query={query}&page=1"
    res = requests.get(url).json()
    results = res.get("results", [])
    results.sort(key=lambda x: x.get("popularity", 0), reverse=True)
    return results[:limit]
