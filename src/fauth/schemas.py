from pydantic import BaseModel, EmailStr, constr
from typing import Optional


class User(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    role: str


class UserCreate(User):
    password: constr(min_length=8)


class UserInDB(User):
    hashed_password: str
    role: str = "user"

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
