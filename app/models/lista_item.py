#app/models/lista_item.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.config import Base

class ListaItemModel(Base):
    __tablename__ = "lista_itens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lista_id = Column(Integer, ForeignKey("listas.id", ondelete="CASCADE"), nullable=False)
    media_type = Column(String, nullable=False)  # "movie", "serie", "anime"
    media_id = Column(Integer, nullable=False)   # id da API
    media_title = Column(String, nullable=False) # salvar nome da mídia

    lista = relationship("ListaModel", back_populates="itens")
