# app/schemas/lista_schema.py
from pydantic import BaseModel, computed_field
from typing import List, Optional

# --- Base ---
class ListaBase(BaseModel):
    nome: str
    description: Optional[str] = None

# --- Criação ---
class ListaCreate(ListaBase):
    user_id: int   # usuário dono da lista

# --- Retorno (com itens) ---
class ListaOut(ListaBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


# --- Base dos itens ---
class ListaItemBase(BaseModel):
    media_type: str   # "movie", "serie", "anime"
    media_id: int     # id vindo da API externa (TMDB, AniList, etc.)
    media_title: str  # nome da mídia


# --- Criação de item ---
class ListaItemCreate(BaseModel):
    lista_id: int
    media_type: str   # "movie", "serie", "anime"
    media_id: int     # id vindo da API externa (TMDB, AniList, etc.)


# --- Retorno de item ---
class ListaItemOut(ListaItemBase):
    id: int
    lista_id: int

    class Config:
        from_attributes = True


# --- Lista com itens dentro ---
class ListaWithItens(ListaOut):
    itens: List[ListaItemOut] = []

    @computed_field
    @property
    def item_count(self) -> int:
        return len(self.itens)


# --- Schemas auxiliares para requests ---
class ListaIdRequest(BaseModel):
    lista_id: int

class UserIdRequest(BaseModel):
    user_id: int

class ItemIdRequest(BaseModel):
    item_id: int

class DeleteItemRequest(BaseModel):
    user_id: int
    lista_id: int
    media_id: int
    media_type: str

# --- Request para deletar lista ---
class DeleteListRequest(BaseModel):
    user_id: int
    lista_id: int