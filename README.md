# Cinelist Backend

O backend do CineList é uma API RESTful construída com FastAPI, que gerencia filmes, séries e animes. Integra PostgreSQL via SQLAlchemy, valida dados com Pydantic e consome informações externas de TMDB e AniList. Permite listagem, busca e avaliação de mídias, garantindo dados consistentes e performance com Uvicorn.

## Tecnologias Utilizadas

- [FastAPI](https://fastapi.tiangolo.com)
- [Pydantic](https://docs.pydantic.dev/latest)
- [Uvicorn](https://www.uvicorn.org)
- [PostgreSQL](https://www.postgresql.org)
- [SQLAlchemy](https://www.sqlalchemy.org)

## Estrutura das pastas
```
cinelist-backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── anime_router.py
│   │   │   ├── media_router.py
│   │   │   ├── movie_router.py
│   │   │   ├── serie_router.py
│   ├── models/
│   │   ├── anime.py
│   │   ├── movie.py
│   │   ├── serie.py
│   ├── schemas/
│   │   ├── requests.py
│   ├── services/
│   │   ├── anilist_service.py
│   │   ├── tmdb_service.py
│   ├── config.py
│   ├── main.py
├── .env
├── requirements.txt

```

## Pré-requisitos

- Python 3.10+
- pip
- PostgreSQL
- SQL Shell
- Git
- Virtualenv (opcional)

## Clone o repositório
```bash
git clone https://github.com/S204-Inatel-2025-2/cinelist-backend.git
```

1. Navegue até o diretório backend:
```bash
cd cinelist-backend
```

2. (Opcional) Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Configuração banco de dados

4. Baixar e instalar o PostgreSQL
Link de download:
[PostgreSQL](https://www.postgresql.org/download/)
- Defina uma senha para o usuário postgres (guarde-a para o próximo passo).
- Mantenha a porta padrão 5432 (a menos que precise alterar).

5. Abra o SQL Shell (psql)
- Insira os dados de conexão (pressione Enter para usar os valores padrão):
```bash
Server [localhost]:
Database [postgres]:
Port [5432]:
Username [postgres]:
Password for user postgres: senha_definida_anteriormente
```

6. Criar banco de dados e usuário para o projeto
```bash
-- Criar banco de dados
CREATE DATABASE cinelist_db;

-- Criar usuário com senha
CREATE USER cinelist_user WITH PASSWORD 'sua_senha_segura';

-- Garantir permissões no banco
GRANT ALL PRIVILEGES ON DATABASE cinelist_db TO cinelist_user;
```
- Substitua sua_senha_segura por uma senha segura e lembre-se de configurá-la no arquivo `.env`.

7. Execute o servidor:
```bash
uvicorn app.main:app --reload
```
> Por padrão, rodará em: http://localhost:8000

### Estrutura do backend

- 📁 api/: inicialização da API e a configuração geral do projeto
- 📁 routes/: define rotas
- 📁 models/: define as classes que representam as tabelas do banco de dados usando SQLAlchemy
- 📁 services/: lógica de negócios
- 📁 schemas/: definição dos modelos de requisição e validação usando Pydantic
- 📄 main.py: ponto de entrada da aplicação


### Endpoints principais

| Método | Rota               | Descrição                                                                           |
| ------ | ------------------ | ----------------------------------------------------------------------------------- |
| GET    | /api/animes        | Lista os 50 animes mais populares                                                   |
| POST   | /api/animes/search | Busca animes por nome usando `SearchRequest`                                        |
| GET    | /api/movies        | Lista os 50 filmes mais populares                                                   |
| POST   | /api/movies/search | Busca filmes por nome usando `SearchRequest`                                        |
| GET    | /api/series        | Lista as 50 séries mais populares                                                   |
| POST   | /api/series/search | Busca séries por nome usando `SearchRequest`                                        |
| GET    | /api/media/popular | Retorna 20 filmes, 20 séries e 20 animes mais populares                             |
| POST   | /api/media/search  | Busca em todas as mídias (filmes, séries e animes) pelo nome usando `SearchRequest` |
| POST   | /api/media/rate    | Avalia uma mídia e salva no banco se necessário usando `RateRequest`                |
| PUT    | /api/media/update  | Atualiza a avaliação de uma mídia já existente usando `UpdateRatingRequest`         |
| DELETE | /api/media/delete  | Remove a avaliação de uma mídia do banco usando `DeleteRequest`                              |
> Acesse http://localhost:8000/docs para a documentação interativa (Swagger UI).
