# app/api/routes/anime_router.py
from fastapi import APIRouter
from app.services.anilist_service import get_top_animes, search_anime

anime_router = APIRouter()

@anime_router.get("/", summary="Top 50 animes populares")
def list_top_animes():
    return get_top_animes(50)

@anime_router.get("/search/{name}", summary="Buscar animes por nome")
def search_animes(name: str):
    return search_anime(name, limit=30)
