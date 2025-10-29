# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
from app.api.routes.auth_router import router as auth_router
from app.api.routes.users_router import users_router

# Cria todas as tabelas no banco (caso não existam)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CineList API")

origins = [
    "http://localhost:5173",  # front-end local (Vite)
    "https://cinelistf.vercel.app"# front-end no vercel
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],             # permite todos os métodos HTTP (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],             # permite todos os headers, incluindo Authorization
)

# Routers separados por tipo de mídia
app.include_router(anime_router, prefix="/anime", tags=["Anime"])
app.include_router(movies_router, prefix="/movies", tags=["Movies"])
app.include_router(series_router, prefix="/series", tags=["Series"])

# Router central para endpoints globais (popular, search e rate)
app.include_router(media_router, prefix="/media", tags=["Media"])

app.include_router(auth_router)
app.include_router(users_router, prefix="/users", tags=["Users"])

@app.get("/")
def root():
    return {"message": "API Online"}
