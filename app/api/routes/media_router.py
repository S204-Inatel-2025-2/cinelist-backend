# app/api/routes/media_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config import get_db
from app.services.tmdb_service import (
    get_popular_movies, get_popular_series,
    get_movie_details, get_series_details,
    get_movie_credits, get_series_credits,
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
from app.schemas.requests import (
    SearchRequest,
    RateRequest,
    UpdateRatingRequest, 
    DeleteRequest,
)

media_router = APIRouter()

# --- Populares ---
@media_router.get("/popular", summary="20 filmes, 20 séries e 20 animes mais populares")
def popular():
    movies = get_popular_movies(20)
    series = get_popular_series(20)
    animes = get_top_animes(20)

    # adiciona o tipo de mídia em cada item
    for m in movies:
        m["type"] = "movie"
    for s in series:
        s["type"] = "series"
    for a in animes:
        a["type"] = "anime"

    # junta tudo
    all_results = movies + series + animes

    # ordena por popularidade (ajuste a chave conforme o nome real no retorno)
    sorted_results = sorted(all_results, key=lambda x: x.get("popularity", 0), reverse=True)

    return {"results": sorted_results}


# --- Busca ---
@media_router.post("/search", summary="Busca por nome da mídia")
def search(req: SearchRequest):
    movies = search_movie(req.name, limit=20)
    series = search_series(req.name, limit=20)
    animes = search_anime(req.name, limit=20)

    # Adiciona o tipo de mídia em cada item
    for m in movies:
        m["type"] = "movie"
    for s in series:
        s["type"] = "series"
    for a in animes:
        a["type"] = "anime"

    # Junta tudo
    all_results = movies + series + animes

    # Ordena por popularidade (ajuste a chave conforme o nome do campo real)
    sorted_results = sorted(all_results, key=lambda x: x.get("popularity", 0), reverse=True)

    return {"results": sorted_results}


# --- Avaliar mídia ---
@media_router.post("/rate", summary="Avalia uma mídia e salva no banco de dados")
def rate(request: RateRequest, db: Session = Depends(get_db)):
    media_type, media_id, rating = request.media_type.lower(), request.media_id, request.rating

    if not 0 <= rating <= 10:
        raise HTTPException(status_code=400, detail="A nota deve estar entre 0 e 10.")

    model_map = {"movie": MovieModel, "serie": SeriesModel, "anime": AnimeModel}
    if media_type not in model_map:
        raise HTTPException(status_code=400, detail="Tipo de mídia inválido")

    model = model_map[media_type]
    item = db.query(model).filter(model.id == media_id).first()

    if item:
        raise HTTPException(
            status_code=409,
            detail=f"{media_type.capitalize()} já foi avaliado. Use PUT para atualizar ou DELETE para remover."
        )

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
            revenue=data.get("revenue"),
            comment=request.comment
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
            comment=request.comment
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
            status=data.get("status"),
            comment=request.comment
        )

    db.add(item)
    db.commit()
    db.refresh(item)
    return {"message": f"{media_type} avaliado", "rating": rating, "title": item.title, "comment": item.comment}


# --- Atualizar avaliação ---
@media_router.put("/rate/update", summary="Atualiza a avaliação de uma mídia já existente")
def update_rating(request: UpdateRatingRequest, db: Session = Depends(get_db)):
    media_type, media_id, rating = request.media_type.lower(), request.media_id, request.rating

    if not 0 <= rating <= 10:
        raise HTTPException(status_code=400, detail="A nota deve estar entre 0 e 10.")

    model_map = {"movie": MovieModel, "serie": SeriesModel, "anime": AnimeModel}
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

    if request.comment is not None:
        item.comment = request.comment

        if media_type == "serie" and (not getattr(item, "creator") or not item.cast):
            credits = get_series_credits(media_id)
            creator = next((p['name'] for p in credits.get('crew', []) if p['job'] == 'Director'), None)
            if not creator:
                data = get_series_details(media_id)
                creator = data.get("created_by")[0]['name'] if data.get("created_by") else None
            item.creator = creator or getattr(item, "creator")

            cast_list = [actor['name'] for actor in credits.get('cast', [])[:10]]
            item.cast = ", ".join(cast_list) if cast_list else item.cast

    db.commit()
    db.refresh(item)
    return {"message": f"Avaliação de {media_type} atualizada", "rating": rating, "title": item.title, "comment": item.comment}


# --- Deletar avaliação ---
@media_router.delete("/rate/delete", summary="Remove a mídia e sua avaliação do banco")
def delete_rating(request: DeleteRequest, db: Session = Depends(get_db)):
    media_type, media_id = request.media_type.lower(), request.media_id

    model_map = {"movie": MovieModel, "serie": SeriesModel, "anime": AnimeModel}
    if media_type not in model_map:
        raise HTTPException(status_code=400, detail="Tipo de mídia inválido")

    model = model_map[media_type]
    item = db.query(model).filter(model.id == media_id).first()

    if not item:
        raise HTTPException(status_code=404, detail=f"{media_type.capitalize()} não encontrado no banco de dados")

    db.delete(item)
    db.commit()
    return {"message": f"{media_type.capitalize()} removido do banco de dados", "title": item.title}
