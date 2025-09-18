# app/api/routes/movie_router.py
from fastapi import APIRouter
from app.services.tmdb_service import get_popular_movies, search_movie
from app.schemas.requests import SearchRequest

movies_router = APIRouter()

@movies_router.get("/", summary="Top 50 filmes populares")
def list_top_movies():
    return get_popular_movies(50)

@movies_router.post("/search", summary="Buscar filmes por nome")
def search_movies(req: SearchRequest):
    return search_movie(req.name, limit=30)