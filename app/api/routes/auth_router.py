from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.config import get_db
from app.models.user import UserModel
from app.models.movie import MovieModel
from app.models.anime import AnimeModel
from app.models.serie import SeriesModel
from app.models.lista import ListaModel
from app.models.lista_item import ListaItemModel
from app.schemas.user_schema import (
    UserOut, UserRegister, UserLogin, TokenResponse, UserUpdateAvatar, UserUpdateUsername
)
from app.core.security import (
    get_password_hash, verify_password,
    create_access_token, get_current_user, oauth2_scheme
)

router = APIRouter(prefix="/auth", tags=["Auth"])

# --- Registro ---
@router.post("/register", response_model=TokenResponse) # <- Retorna TokenResponse
def register_user(user_data: UserRegister, db: Session = Depends(get_db)): # <- Aceita UserRegister
    existing_user_email = db.query(UserModel).filter(UserModel.email == user_data.email).first()
    if existing_user_email:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    existing_user_username = db.query(UserModel).filter(UserModel.username == user_data.name).first()
    if existing_user_username:
        raise HTTPException(status_code=400, detail="Nome de usuário já cadastrado")
    
    if len(user_data.name) < 3:
        raise HTTPException(status_code=400, detail="Nome de usuário não tem o mínimo de caracteres")

    hashed_password = get_password_hash(user_data.password)
    
    # Usa user_data.name para o campo username
    new_user = UserModel(
        username=user_data.name, 
        email=user_data.email, 
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # --- Login automático após registro ---
    token = create_access_token({"sub": str(new_user.id)})
    
    # Converte o modelo SQLAlchemy para o schema Pydantic
    user_out = UserOut.model_validate(new_user) # (ou UserOut.from_orm(new_user) em Pydantic v1)

    return {
        "access_token": token, 
        "token_type": "bearer", 
        "user": user_out 
    }

# --- Login ---
@router.post("/login", response_model=TokenResponse) # <- Retorna TokenResponse
def login(credentials: UserLogin, db: Session = Depends(get_db)): # <- Aceita UserLogin (JSON)
    
    # Busca o usuário pelo email
    user = db.query(UserModel).filter(UserModel.email == credentials.email).first()
    
    # Verifica o usuário e a senha
    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")

    # Cria o token
    token = create_access_token({"sub": str(user.id)})
    
    # Converte o modelo SQLAlchemy para o schema Pydantic
    user_out = UserOut.model_validate(user) # (ou UserOut.from_orm(user) em Pydantic v1)
    
    return {
        "access_token": token, 
        "token_type": "bearer", 
        "user": user_out 
    }

@router.get("/me", response_model=TokenResponse)
def get_profile(
    current_user: UserOut = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
):
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": current_user
    }

@router.put("/me/avatar", response_model=UserOut)
def update_avatar_usuario(
    avatar_data: UserUpdateAvatar,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    current_user.avatar = avatar_data.avatar
    try:
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar o avatar: {e}"
        )
    return current_user

@router.delete("/me", status_code=status.HTTP_200_OK)
def delete_current_user(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user) # Obtém o usuário logado
):
    user_id_to_delete = current_user.id

    try:
        db.query(MovieModel).filter(MovieModel.user_id == user_id_to_delete).delete(synchronize_session=False)
        db.query(SeriesModel).filter(SeriesModel.user_id == user_id_to_delete).delete(synchronize_session=False)
        db.query(AnimeModel).filter(AnimeModel.user_id == user_id_to_delete).delete(synchronize_session=False)

        list_ids = db.query(ListaModel.id).filter(ListaModel.user_id == user_id_to_delete).all()
        list_ids_tuple = [l_id[0] for l_id in list_ids] # Extrai os IDs da tupla
        if list_ids_tuple:
             db.query(ListaItemModel).filter(ListaItemModel.lista_id.in_(list_ids_tuple)).delete(synchronize_session=False)

        db.query(ListaModel).filter(ListaModel.user_id == user_id_to_delete).delete(synchronize_session=False)

        user_to_delete = db.query(UserModel).filter(UserModel.id == user_id_to_delete).first()
        if user_to_delete:
             db.delete(user_to_delete)
        else:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado para exclusão.")

        db.commit()

        return {"message": "Conta deletada com sucesso."}

    except Exception as e:
        db.rollback()
        print(f"Erro ao deletar usuário {user_id_to_delete}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Não foi possível deletar a conta: {e}"
        )
    
@router.put("/me/username", response_model=UserOut)
def update_username(
    user_data: UserUpdateUsername,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    existing_user = db.query(UserModel).filter(
        UserModel.username == user_data.username,
        UserModel.id != current_user.id
    ).first()

    if len(user_data.username) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O nome de usuário deve ter pelo menos 3 caracteres."
        )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome de usuário já em uso. Escolha outro."
        )
    
    current_user.username = user_data.username
    
    try:
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar o nome de usuário: {e}"
        )
        
    return current_user