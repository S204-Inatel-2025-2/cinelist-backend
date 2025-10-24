#app/models/lista_item.py
from sqlalchemy import Column, Integer, String, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from app.config import Base

class ListaItemModel(Base):
    __tablename__ = "lista_itens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lista_id = Column(Integer, ForeignKey("listas.id", ondelete="CASCADE"), nullable=False)
    media_type = Column(String, nullable=False)  # "movie", "serie", "anime"
    media_id = Column(Integer, nullable=False)   # id da API
    media_title = Column(String, nullable=False) # salvar nome da mídia

    poster_path = Column(String, nullable=True)
    backdrop_path = Column(String, nullable=True)
    overview = Column(String, nullable=True)
    vote_average = Column(Float, nullable=True)

    # --- CAMPOS DE DATA ADICIONADOS ---
    # Para que o MediaCard possa exibir o ano
    release_date = Column(String, nullable=True)     # Para Filmes
    first_air_date = Column(String, nullable=True)   # Para Séries
    startDate = Column(JSON, nullable=True)          # Para Animes (AniList envia um objeto)

    lista = relationship("ListaModel", back_populates="itens")
