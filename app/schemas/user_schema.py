# app/schemas/user_schema.py
from pydantic import BaseModel, EmailStr

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdateUsername(BaseModel):
    username: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    avatar: str

    class Config:
        from_attributes = True

class UserPublicOut(BaseModel):
    id: int
    username: str
    avatar: str

    class Config:
        from_attributes = True

# Para a requisição de /register
class UserRegister(BaseModel):
    name: str
    email: str
    password: str

# Para a resposta padronizada de /login e /register
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

class UserUpdateAvatar(BaseModel):
    avatar: str