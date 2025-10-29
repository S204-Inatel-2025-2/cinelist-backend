import requests
import os
import math
import hashlib
from app.core.cache import get_from_cache, set_to_cache

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# --- Duração do Cache (igual ao anilist_service para consistência) ---
CACHE_LIST_TTL = 300      # 5 minutos para listas (populares, busca)
CACHE_DETAILS_TTL = 3600  # 1 hora para detalhes individuais (e créditos)


def _safe_get_request(url: str):
    """
    Função helper para fazer requisições GET ao TMDB com error handling.
    Retorna None em caso de falha.
    """
    try:
        response = requests.get(url)
        response.raise_for_status() # Lança erro para 4xx/5xx
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar dados do TMDB (url: {url}): {e}")
        return None # Retorna None em caso de falha


# --- Populares ---

def get_popular_movies(limit=50):
    cache_key = f"tmdb:popular_movies:{limit}"
    
    cached_data = get_from_cache(cache_key)
    if cached_data:
        return cached_data

    all_results = []
    pages_to_fetch = math.ceil(limit / 20)

    for page in range(1, pages_to_fetch + 1):
        url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=pt-BR&page={page}"
        data = _safe_get_request(url) # Usa a função helper segura
        
        if not data:
            break # Para a execução em caso de erro de rede

        results = data.get("results", [])
        all_results.extend(results)
        
        if len(all_results) >= limit or not results:
            break

    final_results = all_results[:limit]
    
    # Só armazena no cache se a busca foi bem-sucedida
    if final_results:
        set_to_cache(cache_key, final_results, CACHE_LIST_TTL)
        
    return final_results

def get_popular_series(limit=50):
    cache_key = f"tmdb:popular_series:{limit}"
    
    cached_data = get_from_cache(cache_key)
    if cached_data:
        return cached_data
        
    all_results = []
    pages_to_fetch = math.ceil(limit / 20)

    for page in range(1, pages_to_fetch + 1):
        url = f"https://api.themoviedb.org/3/tv/popular?api_key={TMDB_API_KEY}&language=pt-BR&page={page}"
        data = _safe_get_request(url)
        
        if not data:
            break
            
        results = data.get("results", [])
        all_results.extend(results)
        if len(all_results) >= limit or not results:
            break
            
    final_results = all_results[:limit]
    
    if final_results:
        set_to_cache(cache_key, final_results, CACHE_LIST_TTL)
        
    return final_results

# --- Detalhes individuais ---

def get_movie_details(movie_id: int):
    cache_key = f"tmdb:movie_details:{movie_id}"
    
    cached_data = get_from_cache(cache_key)
    if cached_data:
        return cached_data
        
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=pt-BR"
    data = _safe_get_request(url)
    
    # Armazena no cache (mesmo se 'data' for None, para evitar requisições repetidas para 404s)
    # O TTL de detalhes é mais longo
    set_to_cache(cache_key, data, CACHE_DETAILS_TTL)
    
    return data

def get_series_details(series_id: int):
    cache_key = f"tmdb:series_details:{series_id}"
    
    cached_data = get_from_cache(cache_key)
    if cached_data:
        return cached_data
        
    url = f"https://api.themoviedb.org/3/tv/{series_id}?api_key={TMDB_API_KEY}&language=pt-BR"
    data = _safe_get_request(url)
    
    set_to_cache(cache_key, data, CACHE_DETAILS_TTL)
    
    return data

def get_movie_credits(movie_id: int):
    cache_key = f"tmdb:movie_credits:{movie_id}"
    
    cached_data = get_from_cache(cache_key)
    if cached_data:
        return cached_data
        
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={TMDB_API_KEY}&language=pt-BR"
    data = _safe_get_request(url)

    set_to_cache(cache_key, data, CACHE_DETAILS_TTL)
    
    return data

def get_series_credits(series_id: int):
    cache_key = f"tmdb:series_credits:{series_id}"
    
    cached_data = get_from_cache(cache_key)
    if cached_data:
        return cached_data
        
    url = f"https://api.themoviedb.org/3/tv/{series_id}/credits?api_key={TMDB_API_KEY}&language=pt-BR"
    data = _safe_get_request(url)
    
    set_to_cache(cache_key, data, CACHE_DETAILS_TTL)

    return data

# --- Busca por nome ---

def search_movie(query: str, limit=30):
    search_hash = hashlib.sha256(query.encode('utf-8')).hexdigest()
    cache_key = f"tmdb:search_movie:{search_hash}:{limit}"
    
    cached_data = get_from_cache(cache_key)
    if cached_data:
        return cached_data
        
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&language=pt-BR&query={query}&page=1"
    data = _safe_get_request(url)

    if not data:
        return [] # Retorna lista vazia em caso de erro

    results = data.get("results", [])
    results.sort(key=lambda x: x.get("popularity", 0), reverse=True)
    final_results = results[:limit]
    
    # Só cacheia se houver resultados
    if final_results:
        set_to_cache(cache_key, final_results, CACHE_LIST_TTL)
        
    return final_results

def search_series(query: str, limit=30):
    search_hash = hashlib.sha256(query.encode('utf-8')).hexdigest()
    cache_key = f"tmdb:search_series:{search_hash}:{limit}"
    
    cached_data = get_from_cache(cache_key)
    if cached_data:
        return cached_data

    url = f"https://api.themoviedb.org/3/search/tv?api_key={TMDB_API_KEY}&language=pt-BR&query={query}&page=1"
    data = _safe_get_request(url)
    
    if not data:
        return []

    results = data.get("results", [])
    results.sort(key=lambda x: x.get("popularity", 0), reverse=True)
    final_results = results[:limit]
    
    if final_results:
        set_to_cache(cache_key, final_results, CACHE_LIST_TTL)
        
    return final_results