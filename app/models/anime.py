#app/models/anime.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.config import Base
from pydantic import BaseModel

# Modelo SQLAlchemy
class AnimeModel(Base):
    __tablename__ = "anime"

    id = Column(Integer, primary_key=True, autoincrement=True)  # chave interna do banco
    anime_id = Column(Integer, nullable=False)  # ID vindo da API (AniList)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    score = Column(Float, nullable=True)
    release_date = Column(String, nullable=True)
    episodes = Column(Integer, nullable=True)
    status = Column(String, nullable=True)
    comment = Column(String, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("UserModel", back_populates="anime_ratings")


# Schema Pydantic
class AnimeItem(BaseModel):
    id: int
    anime_id: int
    title: str
    description: str | None = ""
    score: float | None = 0.0
    release_date: str | None = None
    episodes: int | None = 0
    status: str | None = None
    comment: str | None = None

    class Config:
        from_attributes = True

