import requests
import time     # Necessário para o timestamp do cache
import hashlib  # Necessário para criar chaves de cache seguras para buscas

ANILIST_URL = "https://graphql.anilist.co"

# --- Cache em memória e Duração ---
# Cache para detalhes individuais
anime_details_cache = {}
# Cache para listas (populares, busca)
anime_list_cache = {}
# Duração para listas (5 minutos)
CACHE_LIST_DURATION_SECONDS = 300
# Duração para detalhes (1 hora)
CACHE_DETAILS_DURATION_SECONDS = 3600

# --- Função _post_query com checagem de erros GraphQL ---
def _post_query(query: str, variables: dict):
    """Faz a requisição POST para a API GraphQL da AniList."""
    try:
        response = requests.post(ANILIST_URL, json={"query": query, "variables": variables})
        response.raise_for_status() # Lança erro para status HTTP 4xx/5xx
        data = response.json()

        # Verifica se a resposta contém a chave 'errors'
        if "errors" in data:
            error_message = data["errors"][0].get("message", "Erro desconhecido na API AniList")
            print(f"Erro GraphQL AniList: {error_message}")
            return {} # Retorna dicionário vazio para sinalizar falha GraphQL

        return data.get("data", {})

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição AniList (HTTP): {e}")
        return {} # Retorna dicionário vazio em caso de erro de rede/HTTP
    except Exception as e: # Captura outros erros (ex: JSON inválido)
        print(f"Erro inesperado ao processar resposta AniList: {e}")
        return {}

# --- Populares (COM CACHING) ---
def get_top_animes(limit=50):
    """Busca os animes mais populares, usando cache."""
    current_time = time.time()
    cache_key = f"top_animes_{limit}"

    # Verifica o cache de listas
    if cache_key in anime_list_cache:
        cached_data, cache_time = anime_list_cache[cache_key]
        if (current_time - cache_time) < CACHE_LIST_DURATION_SECONDS:
            print(f"Retornando animes populares (limite {limit}) do cache.")
            return cached_data

    print(f"Buscando animes populares (limite {limit}) na API AniList.")
    # Se não está no cache ou expirou, busca na API
    query = """
    query ($page: Int, $perPage: Int) {
      Page(page: $page, perPage: $perPage) {
        media(type: ANIME, sort: POPULARITY_DESC) {
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
    # Chama a função _post_query atualizada
    raw_data = _post_query(query, variables)
    page_data = raw_data.get("Page", {})
    results = page_data.get("media", []) if page_data else []

    # Armazena a lista de resultados no cache (apenas se a busca foi bem-sucedida)
    if results: # Só armazena se não houve erro e retornou resultados
        anime_list_cache[cache_key] = (results, current_time)

    return results

# --- Detalhes individuais (COM CACHING) ---
def get_anime_details(anime_id: int):
    """Busca detalhes de um anime, usando cache em memória com TTL."""
    current_time = time.time()

    # Verifica o Cache de detalhes
    if anime_id in anime_details_cache:
        cached_data, cache_time = anime_details_cache[anime_id]
        if (current_time - cache_time) < CACHE_DETAILS_DURATION_SECONDS:
            print(f"Retornando detalhes do anime {anime_id} do cache.")
            return cached_data

    print(f"Buscando detalhes do anime {anime_id} na API AniList.")
    # Se não está no cache ou expirou, busca na API
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
    # Chama _post_query atualizada
    raw_data = _post_query(query, {"id": anime_id})
    media = raw_data.get("Media")

    # Se a API retornou erro ou não encontrou, retorna None (e não cacheia)
    if not media:
        return None

    # Processa os Dados (como antes)
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

    # Armazena no Cache de detalhes
    anime_details_cache[anime_id] = (processed_details, current_time)

    return processed_details

# --- Busca por nome (COM CACHING) ---
def search_anime(name: str, limit=30):
    """Busca animes por nome, usando cache."""
    current_time = time.time()
    search_hash = hashlib.sha256(name.encode('utf-8')).hexdigest()
    cache_key = f"search_anime_{search_hash}_{limit}"

    # Verifica o cache de listas
    if cache_key in anime_list_cache:
        cached_data, cache_time = anime_list_cache[cache_key]
        if (current_time - cache_time) < CACHE_LIST_DURATION_SECONDS:
            print(f"Retornando busca por '{name}' (limite {limit}) do cache.")
            return cached_data

    print(f"Buscando animes por '{name}' (limite {limit}) na API AniList.")
    # Se não está no cache ou expirou, busca na API
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
    # Chama _post_query atualizada
    raw_data = _post_query(query, variables)
    page_data = raw_data.get("Page", {})
    results = page_data.get("media", []) if page_data else []

    # Armazena a lista de resultados no cache (apenas se a busca foi bem-sucedida)
    if results: # Só armazena se não houve erro e retornou resultados
        anime_list_cache[cache_key] = (results, current_time)

    return results