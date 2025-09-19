# app/schemas/resquests.py
from pydantic import BaseModel

# --- Busca ---
class SearchRequest(BaseModel):
    name: str

# --- Avaliações ---
class RateRequest(BaseModel):
    media_type: str
    media_id: int
    rating: float
    comment: str | None = None
    user_id: int

class UpdateRatingRequest(BaseModel):
    media_type: str
    media_id: int
    rating: float
    comment: str | None = None
    user_id: int

class DeleteRequest(BaseModel):
    media_type: str
    media_id: int
    user_id: int