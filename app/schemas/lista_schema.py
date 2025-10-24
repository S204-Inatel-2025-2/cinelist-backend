# app/schemas/lista_schema.py
from pydantic import BaseModel, computed_field
from typing import List, Optional, Any, Union

# --- Base ---
class ListaBase(BaseModel):
    nome: str
    description: Optional[str] = None

# --- Criação ---
class ListaCreate(ListaBase):
    user_id: int

# --- Retorno (sem itens) ---
class ListaOut(ListaBase):
    id: int
    user_id: int
    class Config:
        from_attributes = True

# --- Base dos itens ---
class ListaItemBase(BaseModel):
    media_type: str
    media_id: int
    media_title: str

# --- Criação de item ---
class ListaItemCreate(BaseModel):
    lista_id: int
    media_type: str
    media_id: int

    title: Union[str, dict] # Pode ser string (TMDB) ou dict (AniList)
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    overview: Optional[str] = None
    vote_average: Optional[float] = None
    
    # --- CAMPOS DE DATA ADICIONADOS ---
    release_date: Optional[str] = None
    first_air_date: Optional[str] = None
    startDate: Optional[dict] = None

# --- Retorno de item ---
class ListaItemOut(ListaItemBase):
    id: int
    lista_id: int
    class Config:
        from_attributes = True

# --- SCHEMA PARA RESUMO (usado em /listas/user/get) ---
# Esta classe é necessária para listar todas as listas de forma eficiente
class ListaWithItens(ListaOut):
    itens: List[ListaItemOut] = []
    @computed_field
    @property
    def item_count(self) -> int:
        return len(self.itens)

# --- SCHEMA PARA ITEM DETALHADO (usado em /listas/get) ---
class MediaItemDetailSchema(BaseModel):
    id: int
    title: Union[str, dict]
    name: Optional[str] = None
    overview: Optional[str] = None
    description: Optional[str] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    vote_average: Optional[float] = None
    media_type: str
    release_date: Optional[str] = None
    first_air_date: Optional[str] = None
    startDate: Optional[dict] = None
    class Config:
        from_attributes = True

# --- SCHEMA PARA LISTA DETALHADA (usado em /listas/get) ---
class ListaWithDetailedItens(ListaOut):
    itens: List[MediaItemDetailSchema] = []
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

class DeleteListRequest(BaseModel):
    user_id: int
    lista_id: int