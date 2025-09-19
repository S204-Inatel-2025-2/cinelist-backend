#app/models/lista.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.config import Base

class ListaModel(Base):
    __tablename__ = "listas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # relacionamento com UserModel
    user = relationship("UserModel", back_populates="listas")

    # relacionamento com os itens
    itens = relationship("ListaItemModel", back_populates="lista", cascade="all, delete-orphan")
