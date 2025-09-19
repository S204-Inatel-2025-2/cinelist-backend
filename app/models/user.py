# app/models/user.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.config import Base

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    # relacionamento com avaliações
    movie_ratings = relationship("MovieModel", back_populates="user")
    serie_ratings = relationship("SeriesModel", back_populates="user")
    anime_ratings = relationship("AnimeModel", back_populates="user")
    listas = relationship("ListaModel", back_populates="user", cascade="all, delete-orphan")