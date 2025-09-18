# app/models/serie.py
from sqlalchemy import Column, Integer, String, Float
from app.config import Base
from pydantic import BaseModel

# Modelo SQLAlchemy
class SeriesModel(Base):
    __tablename__ = "series"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    overview = Column(String, nullable=True)
    release_date = Column(String, nullable=True)
    creator = Column(String, nullable=True)
    cast = Column(String, nullable=True)
    episodes = Column(Integer, nullable=True)
    rating = Column(Float, nullable=True)
    status = Column(String, nullable=True)         
    last_episode = Column(String, nullable=True)
    comment = Column(String, nullable=True)     

# Schema Pydantic
class SeriesItem(BaseModel):
    id: int
    title: str
    overview: str | None = ""
    release_date: str | None = None
    creator: str | None = ""
    cast: list[str] | None = []
    rating: float | None = 0.0
    episodes: int | None = 0
    status: str | None = None
    last_episode: str | None = None
    comment: str | None = None

    class Config:
        from_attributes = True
