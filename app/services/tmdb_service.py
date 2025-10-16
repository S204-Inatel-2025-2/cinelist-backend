import requests
import os
import math

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# --- Populares ---
def get_popular_movies(limit=50):
    all_results = []
    # A API do TMDB retorna 20 resultados por página.
    # Calculamos quantas páginas precisamos buscar para atingir o limite.
    pages_to_fetch = math.ceil(limit / 20)

    for page in range(1, pages_to_fetch + 1):
        url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=pt-BR&page={page}"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Lança uma exceção para códigos de erro (4xx ou 5xx)
            data = response.json()
            results = data.get("results", [])
            all_results.extend(results)
            # Para de buscar se já atingimos o limite ou se não há mais resultados
            if len(all_results) >= limit or not results:
                break
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar a página {page} de filmes populares: {e}")
            break # Para a execução em caso de erro de rede

    # Retorna a lista fatiada para garantir que não exceda o limite
    return all_results[:limit]

def get_popular_series(limit=50):
    all_results = []
    pages_to_fetch = math.ceil(limit / 20)

    for page in range(1, pages_to_fetch + 1):
        url = f"https://api.themoviedb.org/3/tv/popular?api_key={TMDB_API_KEY}&language=pt-BR&page={page}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])
            all_results.extend(results)
            if len(all_results) >= limit or not results:
                break
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar a página {page} de séries populares: {e}")
            break
            
    return all_results[:limit]

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
