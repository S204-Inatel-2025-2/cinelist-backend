# app/services/anilist_service.py
import requests

ANILIST_URL = "https://graphql.anilist.co"

def _post_query(query: str, variables: dict):
    try:
        response = requests.post(ANILIST_URL, json={"query": query, "variables": variables})
        response.raise_for_status()
        data = response.json()
        return data.get("data", {})
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição AniList: {e}")
        return {}

# --- Populares ---
def get_top_animes(limit=50):
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
    data = _post_query(query, variables)
    page_data = data.get("Page", {})
    return page_data.get("media", []) if page_data else []

# --- Detalhes individuais ---
def get_anime_details(anime_id):
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
        coverImage { large } # Adicionado
        bannerImage # Adicionado
      }
    }
    """
    data = _post_query(query, {"id": anime_id})
    media = data.get("Media")
    if not media:
        return None

    start_date = media.get("startDate")
    release_date = None
    if start_date and start_date.get("year"):
        release_date = f"{start_date['year']}-{start_date.get('month', 1):02d}-{start_date.get('day', 1):02d}"

    return {
        "id": media.get("id"),
        "title": media.get("title", {}),
        "description": media.get("description") or "",
        "score": 0,
        "release_date": release_date,
        "episodes": media.get("episodes") or 0,
        "status": media.get("status"),
        "coverImage": media.get("coverImage"),    # ADICIONADO
        "bannerImage": media.get("bannerImage"),  # ADICIONADO
    }

# --- Busca por nome ---
def search_anime(name: str, limit=30):
    query = """
    query ($page: Int, $perPage: Int, $search: String) {
      Page(page: $page, perPage: $perPage) {
        media(type: ANIME, search: $search) {
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
    data = _post_query(query, variables)
    page_data = data.get("Page", {})
    return page_data.get("media", []) if page_data else []
