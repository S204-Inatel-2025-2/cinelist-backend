#app/models/movie.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.config import Base
from pydantic import BaseModel

# Modelo SQLAlchemy
class MovieModel(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True, autoincrement=True)
    movie_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    overview = Column(String)
    release_date = Column(String, nullable=True)
    director = Column(String, nullable=True)
    cast = Column(String, nullable=True)
    runtime = Column(Integer, nullable=True)
    budget = Column(Float, nullable=True)
    revenue = Column(Float, nullable=True)
    rating = Column(Float, nullable=True)
    comment = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # ADICIONADO: Campos para as imagens
    poster_path = Column(String, nullable=True)
    backdrop_path = Column(String, nullable=True)
    
    user = relationship("UserModel", back_populates="movie_ratings")

# Schema Pydantic
class MovieItem(BaseModel):
    id: int
    movie_id: int
    title: str
    overview: str | None = ""
    release_date: str | None = None
    director: str | None = ""
    cast: list[str] | None = []
    rating: float | None = 0.0
    runtime: int | None = 0
    budget: float | None = 0.0
    revenue: float | None = 0.0
    comment: str | None = None
    
    # ADICIONADO: Campos para as imagens
    poster_path: str | None = None
    backdrop_path: str | None = None

    class Config:
        from_attributes = True