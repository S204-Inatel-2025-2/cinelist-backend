# app/api/routes/media_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config import get_db
from app.services.tmdb_service import (
    get_popular_movies,
    get_popular_series,
    get_movie_details,
    get_series_details,
    get_movie_credits,
    get_series_credits,
    search_movie,
    search_series,
)
from app.services.anilist_service import (
    get_top_animes,
    get_anime_details,
    search_anime,
)
from app.models.movie import MovieModel
from app.models.serie import SeriesModel
from app.models.anime import AnimeModel

media_router = APIRouter()

# --- Populares ---
@media_router.get("/popular", summary="20 filmes, 20 séries e 20 animes mais populares")
def popular():
    movies = get_popular_movies(20)
    series = get_popular_series(20)
    animes = get_top_animes(20)
    return {"movies": movies, "series": series, "animes": animes}

# --- Busca ---
@media_router.get("/search/{name}", summary="Busca por nome da mídia")
def search(name: str):
    movies = search_movie(name, limit=20)
    series = search_series(name, limit=20)
    animes = search_anime(name, limit=20)
    return {"movies": movies, "series": series, "animes": animes}

# --- POST Avaliação ---
@media_router.post("/rate/{media_type}/{media_id}", summary="Avalia uma mídia e salva no banco de dados")
def rate(media_type: str, media_id: int, rating: float, db: Session = Depends(get_db)):
    # --- Validação de faixa de notas ---
    if not 0 <= rating <= 10:
        raise HTTPException(status_code=400, detail="A nota deve estar entre 0 e 10.")

    model_map = {
        "movie": MovieModel,
        "serie": SeriesModel,
        "anime": AnimeModel
    }

    if media_type not in model_map:
        raise HTTPException(status_code=400, detail="Tipo de mídia inválido")

    model = model_map[media_type]
    item = db.query(model).filter(model.id == media_id).first()

    # --- Impede avaliação duplicada ---
    if item:
        raise HTTPException(
            status_code=409,
            detail=f"{media_type.capitalize()} já foi avaliado. Use PUT para atualizar ou DELETE para remover."
        )

    if not item:
        if media_type == "movie":
            data = get_movie_details(media_id)
            credits = get_movie_credits(media_id)
            director = next((p['name'] for p in credits.get('crew', []) if p['job'] == 'Director'), None)
            cast = ", ".join([actor['name'] for actor in credits.get('cast', [])[:10]])

            item = MovieModel(
                id=data["id"],
                title=data["title"],
                overview=data.get("overview", ""),
                release_date=data.get("release_date"),
                director=director,
                cast=cast,
                rating=rating,
                runtime=data.get("runtime"),
                budget=data.get("budget"),
                revenue=data.get("revenue")
            )

        elif media_type == "serie":
            data = get_series_details(media_id)
            credits = get_series_credits(media_id)
            creator = next(
                (p['name'] for p in credits.get('crew', []) if p['job'] == 'Director'),
                data.get("created_by")[0]['name'] if data.get("created_by") else None
            )
            cast_list = [actor['name'] for actor in credits.get('cast', [])[:10]]
            cast = ", ".join(cast_list) if cast_list else None

            item = SeriesModel(
            id=data["id"],
            title=data["name"],
            overview=data.get("overview", ""),
            release_date=data.get("first_air_date"),
            creator=creator,
            cast=cast,
            rating=rating,
            episodes=data.get("number_of_episodes"),
            status=data.get("status"),
            last_episode=data.get("last_air_date"),
        )


        elif media_type == "anime":
            data = get_anime_details(media_id)
            if not data:
                raise HTTPException(status_code=404, detail="Anime não encontrado na API")

            item = AnimeModel(
                id=data["id"],
                title=data["title"].get("romaji") or data["title"].get("english") or "Unknown",
                description=data.get("description", ""),
                score=rating,
                release_date=data.get("release_date"),
                episodes=data.get("episodes"),
                status=data.get("status")
            )

        db.add(item)
    else:
        if media_type == "anime":
            item.score = rating
        else:
            item.rating = rating

    db.commit()
    db.refresh(item)
    return {"message": f"{media_type} avaliado", "rating": rating, "title": item.title}


# --- PUT: Atualizar avaliação ---
@media_router.put("/rate/{media_type}/{media_id}", summary="Atualiza a avaliação de uma mídia já existente")
def update_rating(media_type: str, media_id: int, rating: float, db: Session = Depends(get_db)):
    # --- Validação de faixa de notas ---
    if not 0 <= rating <= 10:
        raise HTTPException(status_code=400, detail="A nota deve estar entre 0 e 10.")

    model_map = {
        "movie": MovieModel,
        "serie": SeriesModel,
        "anime": AnimeModel
    }

    if media_type not in model_map:
        raise HTTPException(status_code=400, detail="Tipo de mídia inválido")

    model = model_map[media_type]
    item = db.query(model).filter(model.id == media_id).first()

    if not item:
        raise HTTPException(status_code=404, detail=f"{media_type.capitalize()} não encontrado no banco de dados")

    if media_type == "anime":
        item.score = rating
    else:
        item.rating = rating

        if media_type == "serie" and (not getattr(item, "creator") or not item.cast):
            credits = get_series_credits(media_id)
            creator = next(
                (p['name'] for p in credits.get('crew', []) if p['job'] == 'Director'),
                None
            )
            if not creator:
                data = get_series_details(media_id)
                creator = data.get("created_by")[0]['name'] if data.get("created_by") else None
            item.creator = creator or getattr(item, "creator")

            cast_list = [actor['name'] for actor in credits.get('cast', [])[:10]]
            item.cast = ", ".join(cast_list) if cast_list else item.cast

    db.commit()
    db.refresh(item)
    return {"message": f"Avaliação de {media_type} atualizada", "rating": rating, "title": item.title}

# --- DELETE Avaliação ---
@media_router.delete("/rate/{media_type}/{media_id}", summary="Remove a mídia e sua avaliação do banco")
def delete_rating(media_type: str, media_id: int, db: Session = Depends(get_db)):
    model_map = {
        "movie": MovieModel,
        "serie": SeriesModel,
        "anime": AnimeModel
    }

    if media_type not in model_map:
        raise HTTPException(status_code=400, detail="Tipo de mídia inválido")

    model = model_map[media_type]
    item = db.query(model).filter(model.id == media_id).first()

    if not item:
        raise HTTPException(status_code=404, detail=f"{media_type.capitalize()} não encontrado no banco de dados")

    db.delete(item)
    db.commit()
    return {"message": f"{media_type.capitalize()} removido do banco de dados", "title": item.title}
