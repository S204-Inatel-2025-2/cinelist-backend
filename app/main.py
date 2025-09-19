# app/main.py
from fastapi import FastAPI
from app.config import Base, engine
from app.models.user import UserModel
from app.models.movie import MovieModel
from app.models.anime import AnimeModel
from app.models.serie import SeriesModel
from app.models.lista import ListaModel
from app.models.lista_item import ListaItemModel
from app.api.routes.anime_router import anime_router
from app.api.routes.movie_router import movies_router
from app.api.routes.serie_router import series_router
from app.api.routes.media_router import media_router

# Cria todas as tabelas no banco (caso não existam)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CineList API")

# Routers separados por tipo de mídia
app.include_router(anime_router, prefix="/anime", tags=["Anime"])
app.include_router(movies_router, prefix="/movies", tags=["Movies"])
app.include_router(series_router, prefix="/series", tags=["Series"])

# Router central para endpoints globais (popular, search e rate)
app.include_router(media_router, prefix="/media", tags=["Media"])

@app.get("/")
def root():
    return {"message": "API Online"}
