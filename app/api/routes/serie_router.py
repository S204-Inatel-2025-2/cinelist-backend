# app/api/routes/serie_router.py
from fastapi import APIRouter
from app.services.tmdb_service import get_popular_series, search_series

series_router = APIRouter()

@series_router.get("/", summary="Top 50 séries populares")
def list_top_series():
    return get_popular_series(50)

@series_router.get("/search/{name}", summary="Buscar séries por nome")
def search_series_route(name: str):
    return search_series(name, limit=30)

