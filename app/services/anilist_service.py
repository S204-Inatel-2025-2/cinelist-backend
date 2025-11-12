# app/services/anilist_service.py
import requests
import hashlib 
from app.core.cache import get_from_cache, set_to_cache

ANILIST_URL = "https://graphql.anilist.co"

# --- Duração do Cache ---
CACHE_LIST_TTL = 300      # 5 minutos para listas (populares, busca)
CACHE_DETAILS_TTL = 3600  # 1 hora para detalhes individuais

def _post_query(query: str, variables: dict):
    """Faz a requisição POST para a API GraphQL da AniList."""
    try:
        response = requests.post(ANILIST_URL, json={"query": query, "variables": variables})
        response.raise_for_status()
        data = response.json()

        if "errors" in data:
            error_message = data["errors"][0].get("message", "Erro desconhecido na API AniList")
            print(f"Erro GraphQL AniList: {error_message}")
            return {} 

        return data.get("data", {})

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição AniList (HTTP): {e}")
        return {}
    except Exception as e:
        print(f"Erro inesperado ao processar resposta AniList: {e}")
        return {}

# --- Populares ---
def get_top_animes(limit=50):
    """Busca os animes mais populares, usando cache Redis."""
    cache_key = f"anilist:trending_animes:{limit}"

    cached_data = get_from_cache(cache_key)
    if cached_data:
        return cached_data

    query = """
    query ($page: Int, $perPage: Int) {
      Page(page: $page, perPage: $perPage) {
        media(type: ANIME, sort: TRENDING_DESC) {
          id
          title { romaji english }
          description(asHtml: false)
          startDate { year month day }
          coverImage { large medium }
          bannerImage
          averageScore
          genres
        }
      }
    }
    """
    variables = {"page": 1, "perPage": limit}
    raw_data = _post_query(query, variables)
    page_data = raw_data.get("Page", {})
    results = page_data.get("media", []) if page_data else []

    if results:
        set_to_cache(cache_key, results, CACHE_LIST_TTL)

    return results

# --- Detalhes individuais ---
def get_anime_details(anime_id: int):
    """Busca detalhes de um anime, usando cache Redis com TTL."""
    cache_key = f"anilist:details:{anime_id}"
    
    cached_data = get_from_cache(cache_key)
    if cached_data:
        return cached_data

    query = """
    query ($id: Int) {
      Media(id: $id, type: ANIME) {
        id
        title { romaji english }
        description(asHtml: false)
        averageScore
        startDate { year month day }
        episodes
        status
        coverImage { large }
        bannerImage
      }
    }
    """
    raw_data = _post_query(query, {"id": anime_id})
    media = raw_data.get("Media")

    if not media:
        return None # Não armazena nada no cache se não encontrar

    # Processa os Dados
    start_date = media.get("startDate")
    release_date = None
    if start_date and start_date.get("year"):
        release_date = f"{start_date['year']}-{start_date.get('month', 1):02d}-{start_date.get('day', 1):02d}"

    cover_image_obj = media.get("coverImage", {}) or {}
    poster_url = cover_image_obj.get("large")

    processed_details = {
        "id": media.get("id"),
        "title": media.get("title", {}),
        "description": media.get("description") or "",
        "vote_average": (media.get("averageScore") or 0) / 10.0,
        "release_date": release_date,
        "episodes": media.get("episodes") or 0,
        "status": media.get("status"),
        "poster_path": poster_url,
        "backdrop_path": media.get("bannerImage"),
    }

    set_to_cache(cache_key, processed_details, CACHE_DETAILS_TTL)

    return processed_details

# --- Busca por nome ---
def search_anime(name: str, limit=30):
    """Busca animes por nome, usando cache Redis."""
    search_hash = hashlib.sha256(name.encode('utf-8')).hexdigest()
    cache_key = f"anilist:search:{search_hash}:{limit}"

    cached_data = get_from_cache(cache_key)
    if cached_data:
        return cached_data

    query = """
    query ($page: Int, $perPage: Int, $search: String) {
      Page(page: $page, perPage: $perPage) {
        media(type: ANIME, search: $search, sort: [POPULARITY_DESC]) {
          id
          title { romaji english }
          description(asHtml: false)
          startDate { year month day }
          coverImage { large medium }
          bannerImage
          averageScore
          genres
        }
      }
    }
    """
    variables = {"page": 1, "perPage": limit, "search": name}
    raw_data = _post_query(query, variables)
    page_data = raw_data.get("Page", {})
    results = page_data.get("media", []) if page_data else []

    if results:
        set_to_cache(cache_key, results, CACHE_LIST_TTL)

    return results