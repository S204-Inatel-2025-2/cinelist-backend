# app/api/routes/movie_router.py
from fastapi import APIRouter
from app.services.tmdb_service import get_popular_movies, search_movie

movies_router = APIRouter()

@movies_router.get("/", summary="Top 50 filmes populares")
def list_top_movies():
    return get_popular_movies(50)

@movies_router.get("/search/{name}", summary="Buscar filmes por nome")
def search_movies(name: str):
    return search_movie(name, limit=30)