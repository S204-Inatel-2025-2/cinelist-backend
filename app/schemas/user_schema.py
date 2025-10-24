# app/schemas/user_schema.py
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True

# Para a requisição de /register
class UserRegister(BaseModel):
    name: str
    email: str
    password: str

# Para a requisição de /login
class UserLogin(BaseModel):
    email: str
    password: str

# Para a resposta padronizada de /login e /register
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserOut