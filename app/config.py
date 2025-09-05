# app/config.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Cria o engine do SQLAlchemy que representa a conexão com o banco de dados
engine = create_engine(DATABASE_URL)

# Fábrica de sessões ligados ao engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe base para modelos ORM
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db # fornece a sessão para o endpoint
    finally: # garante o fechamento da sessão
        db.close()
