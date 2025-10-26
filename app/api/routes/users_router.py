# app/routers/users_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.config import get_db
from app.models.user import UserModel
from app.schemas.user_schema import UserPublicOut
from app.core.security import get_current_user

# Novo router com prefixo /users
users_router = APIRouter()

@users_router.get("/get", response_model=List[UserPublicOut])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    users = db.query(UserModel).filter(
        UserModel.id != current_user.id
    ).order_by(UserModel.username).all()
    
    return users