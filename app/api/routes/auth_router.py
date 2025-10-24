from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config import get_db
from app.models.user import UserModel
from app.schemas.user_schema import UserOut, UserRegister, UserLogin, TokenResponse
from app.core.security import (
    get_password_hash, verify_password,
    create_access_token, decode_access_token
)

router = APIRouter(prefix="/auth", tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# --- Registro ---
@router.post("/register", response_model=TokenResponse) # <- Retorna TokenResponse
def register_user(user_data: UserRegister, db: Session = Depends(get_db)): # <- Aceita UserRegister
    existing_user = db.query(UserModel).filter(UserModel.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

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

# --- Dependência para rotas protegidas ---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    
    # Validação robusta de user_id
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: 'sub' não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(UserModel).filter(UserModel.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return user

@router.get("/me") # <- response_model removido para permitir dict
def get_profile(current_user: UserOut = Depends(get_current_user)):
    # Retorna o usuário aninhado, como o frontend espera
    return {"user": current_user}