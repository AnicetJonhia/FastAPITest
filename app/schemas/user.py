from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import RoleEnum

class UserCreate(BaseModel):
    username: str
    full_name: Optional[str]
    email: EmailStr
    password: str
    role: RoleEnum
    department_id: Optional[int]

class UserOut(BaseModel):
    id: int
    username: str
    full_name: Optional[str]
    email: EmailStr
    role: RoleEnum
    department_id: Optional[int]

    class Config:
        orm_mode = True



class UserUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[RoleEnum] = None
    department_id: Optional[int] = None


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None  # email
    role: Optional[str] = None
