# Cinelist Backend

> **Acesse o projeto online:** [CineList](https://mycinelist.vercel.app/home)

Uma API completa para gestão de listas, avaliações e catálogo de filmes, séries e animes, integrada a TMDB e AniList.

---

## Sobre o Projeto

O **CineList** é uma plataforma para explorar, avaliar e organizar mídias de diferentes categorias.  
A API oferece recursos para:

- Buscar filmes, séries e animes  
- Obter detalhes com base em APIs externas  
- Criar listas personalizadas  
- Atribuir notas e comentários  
- Gerenciar usuários e perfis  
- Fazer upload de avatar  

O objetivo é fornecer uma base sólida e extensível para aplicações de catálogo multimídia.


## Tecnologias Utilizadas

- [FastAPI](https://fastapi.tiangolo.com)
- [Pydantic](https://docs.pydantic.dev/latest)
- [Uvicorn](https://www.uvicorn.org)
- [PostgreSQL](https://www.postgresql.org)
- [Supabase](https://supabase.com)
- [Redis](https://redis.io)
- [SQLAlchemy](https://www.sqlalchemy.org)
- [JWT](https://www.jwt.io)

## Estrutura das pastas
```
cinelist-backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── anime_router.py
│   │   │   ├── auth_router.py
│   │   │   ├── media_router.py
│   │   │   ├── movie_router.py
│   │   │   ├── serie_router.py
│   │   │   ├── users_router.py
│   ├── core/
│   │   ├── cache.py
│   │   ├── security.py
│   ├── models/
│   │   ├── anime.py
│   │   ├── movie.py
│   │   ├── serie.py
│   │   ├── user.py
│   │   ├── lista.py
│   │   ├── lista_item.py
│   ├── schemas/
│   │   ├── requests.py
│   │   ├── user_schema.py
│   │   ├── lista_schema.py
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
- 📁 core/: gerenciamento do cache, autenticação e segurança da API
- 📄 main.py: ponto de entrada da aplicação


## API Endpoints

### 🔐 Autenticação & Usuários

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Registra um novo usuário e retorna o token (`UserRegister`). |
| `POST` | `/api/auth/login` | Realiza login e retorna o token de acesso (`UserLogin`). |
| `GET` | `/api/auth/me` | Retorna o perfil do usuário autenticado. |
| `PUT` | `/api/auth/me/avatar` | Atualiza o avatar do usuário autenticado (`UserUpdateAvatar`). |
| `PUT` | `/api/auth/me/username` | Atualiza o nome de usuário (`UserUpdateUsername`). |
| `DELETE` | `/api/auth/me` | Exclui a conta do usuário logado e todos os seus dados. |
| `GET` | `/api/users/get` | Lista todos os usuários da plataforma (exceto o logado). |
| `GET` | `/api/users/{user_id}` | Retorna o perfil público de um usuário específico pelo ID. |

### 🎬 Mídia (Geral e Avaliações)

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| `GET` | `/api/media/popular` | Retorna um mix das 20 mídias mais populares de cada categoria. |
| `POST` | `/api/media/search` | Busca global em Filmes, Séries e Animes (`SearchRequest`). |
| `POST` | `/api/media/rate` | Avalia/Salva uma mídia no banco de dados (`RateRequest`). |
| `POST` | `/api/media/rate/user/get` | Retorna todas as mídias avaliadas por um usuário (`UserIdRequest`). |
| `PUT` | `/api/media/rate/update` | Atualiza a nota ou comentário de uma avaliação (`UpdateRatingRequest`). |
| `DELETE` | `/api/media/rate/delete` | Remove uma avaliação e a mídia do banco (`DeleteRequest`). |

### 📝 Listas Personalizadas

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| `POST` | `/api/media/listas/create` | Cria uma nova lista vazia (`ListaCreate`). |
| `POST` | `/api/media/listas/get` | Retorna os detalhes e itens de uma lista (`ListaIdRequest`). |
| `POST` | `/api/media/listas/user/get` | Retorna todas as listas de um usuário (`UserIdRequest`). |
| `DELETE` | `/api/media/listas/delete` | Deleta uma lista e todos os seus itens (`DeleteListRequest`). |
| `POST` | `/api/media/listas/item/add` | Adiciona uma mídia dentro de uma lista (`ListaItemCreate`). |
| `DELETE` | `/api/media/listas/item/delete` | Remove um item específico de uma lista (`DeleteItemRequest`). |

### 📺 Catálogo Específico

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| `GET` | `/api/animes` | Top 50 Animes populares. |
| `POST` | `/api/animes/search` | Busca específica de Animes (`SearchRequest`). |
| `GET` | `/api/movies` | Top 50 Filmes populares. |
| `POST` | `/api/movies/search` | Busca específica de Filmes (`SearchRequest`). |
| `GET` | `/api/series` | Top 50 Séries populares. |
| `POST` | `/api/series/search` | Busca específica de Séries (`SearchRequest`). |


## Banco de Dados

### Principais tabelas:

- users
- media_items
- ratings
- lists
- list_items


## Licença

Este projeto está sob a licença [MIT](https://github.com/S204-Inatel-2025-2/cinelist-backend/blob/main/LICENSE).