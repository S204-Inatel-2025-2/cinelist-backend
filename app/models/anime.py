#app/models/anime.py
from sqlalchemy import Column, Integer, String, Float
from app.config import Base
from pydantic import BaseModel

# Modelo SQLAlchemy
class AnimeModel(Base):
    __tablename__ = "anime"
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    score = Column(Float, nullable=True)
    release_date = Column(String, nullable=True)
    episodes = Column(Integer, nullable=True)
    status = Column(String, nullable=True)
    comment = Column(String, nullable=True)

# Schema Pydantic
class AnimeItem(BaseModel):
    id: int
    title: str
    description: str | None = ""
    score: float | None = 0.0
    release_date: str | None = None
    episodes: int | None = 0
    status: str | None = None
    comment: str | None = None

    class Config:
        from_attributes = True

