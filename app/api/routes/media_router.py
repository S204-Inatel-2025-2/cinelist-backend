# app/api/routes/media_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
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
from app.models.user import UserModel
from app.models.lista import ListaModel
from app.models.lista_item import ListaItemModel
from app.schemas.requests import (
    SearchRequest,
    RateRequest,
    UpdateRatingRequest, 
    DeleteRequest,
)
from app.schemas.lista_schema import (
    ListaCreate, 
    ListaOut, 
    ListaWithItens, 
    ListaItemCreate, 
    ListaItemOut, 
    ItemIdRequest, 
    ListaIdRequest, 
    UserIdRequest,
    DeleteItemRequest,
    DeleteListRequest,
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
    media_type = request.media_type.lower()
    media_id = request.media_id
    rating = request.rating
    user_id = request.user_id

    # Verifica se o usuário existe
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if not 0 <= rating <= 10:
        raise HTTPException(status_code=400, detail="A nota deve estar entre 0 e 10.")

    model_map = {"movie": MovieModel, "serie": SeriesModel, "anime": AnimeModel}
    if media_type not in model_map:
        raise HTTPException(status_code=400, detail="Tipo de mídia inválido")

    model = model_map[media_type]

    # Verifica se já existe avaliação
    if media_type == "anime":
        item = db.query(model).filter(model.anime_id == media_id, model.user_id == user_id).first()
    elif media_type == "movie":
        item = db.query(model).filter(model.movie_id == media_id, model.user_id == user_id).first()
    else:  # serie
        item = db.query(model).filter(model.movie_id == media_id, model.user_id == user_id).first()
    if item:
        raise HTTPException(
            status_code=409,
            detail=f"{media_type.capitalize()} já foi avaliado por este usuário. Use PUT para atualizar ou DELETE para remover."
        )

    # --- Criação do item por tipo ---
    if media_type == "movie":
        data = get_movie_details(media_id)
        credits = get_movie_credits(media_id)
        director = next((p['name'] for p in credits.get('crew', []) if p['job'] == 'Director'), None)
        cast = ", ".join([actor['name'] for actor in credits.get('cast', [])[:10]])

        item = MovieModel(
            movie_id=data["id"],
            title=data["title"],
            overview=data.get("overview", ""),
            release_date=data.get("release_date"),
            director=director,
            cast=cast,
            rating=rating,
            runtime=data.get("runtime"),
            budget=data.get("budget"),
            revenue=data.get("revenue"),
            comment=request.comment,
            user_id=user_id,
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
            movie_id=data["id"],
            title=data["name"],
            overview=data.get("overview", ""),
            release_date=data.get("first_air_date"),
            creator=creator,
            cast=cast,
            rating=rating,
            episodes=data.get("number_of_episodes"),
            status=data.get("status"),
            last_episode=data.get("last_air_date"),
            comment=request.comment,
            user_id=user_id,
        )

    elif media_type == "anime":
        data = get_anime_details(media_id)
        if not data:
            raise HTTPException(status_code=404, detail="Anime não encontrado na API")

        item = AnimeModel(
            anime_id=data["id"],
            title=data["title"].get("romaji") or data["title"].get("english") or "Unknown",
            description=data.get("description", ""),
            score=rating,
            release_date=data.get("release_date"),
            episodes=data.get("episodes"),
            status=data.get("status"),
            comment=request.comment,
            user_id=user_id,
        )

    db.add(item)
    db.commit()
    db.refresh(item)

    return {
        "message": f"{media_type} avaliado",
        "id": item.id,
        "title": item.title,
        "rating": rating,
        "comment": item.comment,
        "type": media_type
    }


# --- Atualizar avaliação ---
@media_router.put("/rate/update", summary="Atualiza a avaliação de uma mídia já existente")
def update_rating(request: UpdateRatingRequest, db: Session = Depends(get_db)):
    media_type = request.media_type.lower()
    media_id = request.media_id
    rating = request.rating
    user_id = request.user_id

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if not 0 <= rating <= 10:
        raise HTTPException(status_code=400, detail="A nota deve estar entre 0 e 10.")

    model_map = {"movie": MovieModel, "serie": SeriesModel, "anime": AnimeModel}
    if media_type not in model_map:
        raise HTTPException(status_code=400, detail="Tipo de mídia inválido")

    model = model_map[media_type]
    
    if media_type == "anime":
        item = db.query(model).filter(model.anime_id == media_id, model.user_id == user_id).first()
    elif media_type == "movie":
        item = db.query(model).filter(model.movie_id == media_id, model.user_id == user_id).first()
    else:  # serie
        item = db.query(model).filter(model.movie_id == media_id, model.user_id == user_id).first()

    if not item:
        raise HTTPException(status_code=404, detail=f"{media_type.capitalize()} não encontrado no banco de dados para este usuário")

    # Atualiza nota
    if media_type == "anime":
        item.score = rating
    else:
        item.rating = rating

    # Atualiza comentário
    if request.comment is not None:
        item.comment = request.comment

    db.commit()
    db.refresh(item)

    return {
        "message": f"Avaliação de {media_type} atualizada",
        "id": item.id,
        "title": item.title,
        "rating": rating,
        "comment": item.comment,
        "type": media_type
    }

# --- Deletar avaliação ---
@media_router.delete("/rate/delete", summary="Remove a mídia e sua avaliação do banco")
def delete_rating(request: DeleteRequest, db: Session = Depends(get_db)):
    media_type = request.media_type.lower()
    media_id = request.media_id
    user_id = request.user_id

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    model_map = {"movie": MovieModel, "serie": SeriesModel, "anime": AnimeModel}
    if media_type not in model_map:
        raise HTTPException(status_code=400, detail="Tipo de mídia inválido")

    model = model_map[media_type]
    if media_type == "anime":
        item = db.query(model).filter(model.anime_id == media_id, model.user_id == user_id).first()
    elif media_type == "movie":
        item = db.query(model).filter(model.movie_id == media_id, model.user_id == user_id).first()
    else:  # serie
        item = db.query(model).filter(model.movie_id == media_id, model.user_id == user_id).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"{media_type.capitalize()} não encontrado no banco de dados para este usuário")

    db.delete(item)
    db.commit()

    return {
        "message": f"{media_type.capitalize()} removido do banco de dados",
        "id": media_id,
        "title": item.title,
        "type": media_type
    }


# --- Criar lista ---
@media_router.post("/listas/create", response_model=ListaOut, summary="Cria uma nova lista para o usuário")
def create_lista(request: ListaCreate, db: Session = Depends(get_db)):
    # Verifica se o usuário existe
    user = db.query(UserModel).filter(UserModel.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    nova_lista = ListaModel(nome=request.nome, user_id=request.user_id)
    db.add(nova_lista)
    db.commit()
    db.refresh(nova_lista)
    return nova_lista


# --- Adicionar item na lista ---
@media_router.post("/listas/item/add", response_model=ListaItemOut, summary="Adiciona uma mídia em uma lista")
def add_item(request: ListaItemCreate, db: Session = Depends(get_db)):
    lista = db.query(ListaModel).filter(ListaModel.id == request.lista_id).first()
    if not lista:
        raise HTTPException(status_code=404, detail="Lista não encontrada")

    # Verifica duplicação (não deixar adicionar a mesma mídia duas vezes na mesma lista)
    existente = db.query(ListaItemModel).filter(
        ListaItemModel.lista_id == request.lista_id,
        ListaItemModel.media_id == request.media_id,
        ListaItemModel.media_type == request.media_type
    ).first()
    if existente:
        raise HTTPException(status_code=409, detail="Essa mídia já está na lista")

    # Obter título da mídia a partir da API
    if request.media_type == "movie":
        data = get_movie_details(request.media_id)
        if not data:
            raise HTTPException(status_code=404, detail="Filme não encontrado na API")
        media_title = data.get("title")
    elif request.media_type == "serie":
        data = get_series_details(request.media_id)
        if not data:
            raise HTTPException(status_code=404, detail="Série não encontrada na API")
        media_title = data.get("name")
    elif request.media_type == "anime":
        data = get_anime_details(request.media_id)
        if not data:
            raise HTTPException(status_code=404, detail="Anime não encontrado na API")
        media_title = data["title"].get("romaji") or data["title"].get("english") or "Unknown"
    else:
        raise HTTPException(status_code=400, detail="Tipo de mídia inválido")

    novo_item = ListaItemModel(
        lista_id=request.lista_id,
        media_type=request.media_type,
        media_id=request.media_id,
        media_title=media_title
    )
    db.add(novo_item)
    db.commit()
    db.refresh(novo_item)
    return novo_item


# --- Remover item da lista ---
@media_router.delete("/listas/item/delete", summary="Remove uma mídia de uma lista")
def delete_item(request: DeleteItemRequest, db: Session = Depends(get_db)):
    # Verifica se a lista pertence ao usuário
    lista = db.query(ListaModel).filter(
        ListaModel.id == request.lista_id,
        ListaModel.user_id == request.user_id
    ).first()
    if not lista:
        raise HTTPException(status_code=404, detail="Lista não encontrada para este usuário")
    
    # Busca o item dentro da lista
    item = db.query(ListaItemModel).filter(
        ListaItemModel.lista_id == request.lista_id,
        ListaItemModel.media_id == request.media_id,
        ListaItemModel.media_type == request.media_type
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado na lista")
    
    db.delete(item)
    db.commit()
    return {"message": "Item removido da lista", "media_id": request.media_id,  "media_type": request.media_type, "lista_id": request.lista_id}


# --- Obter lista com itens ---
@media_router.post("/listas/get", response_model=ListaWithItens, summary="Retorna uma lista com seus itens")
def get_lista(request: ListaIdRequest, db: Session = Depends(get_db)):
    lista = db.query(ListaModel).filter(ListaModel.id == request.lista_id).first()
    if not lista:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    return lista


# --- Listar todas as listas de um usuário com itens ---
@media_router.post("/listas/user/get", response_model=List[ListaWithItens], summary="Retorna todas as listas de um usuário com seus itens")
def get_listas_by_user(request: UserIdRequest, db: Session = Depends(get_db)):
    listas = db.query(ListaModel).filter(ListaModel.user_id == request.user_id).all()
    return listas

# --- Deletar lista e todos os itens ---
@media_router.delete("/listas/delete", summary="Remove uma lista e todos os itens dela")
def delete_lista(request: DeleteListRequest, db: Session = Depends(get_db)):
    # Verifica se a lista pertence ao usuário
    lista = db.query(ListaModel).filter(
        ListaModel.id == request.lista_id,
        ListaModel.user_id == request.user_id
    ).first()
    if not lista:
        raise HTTPException(status_code=404, detail="Lista não encontrada para este usuário")

    db.delete(lista)
    db.commit()

    return {
        "message": "Lista removida com todos os itens",
        "lista_id": request.lista_id,
        "user_id": request.user_id
    }