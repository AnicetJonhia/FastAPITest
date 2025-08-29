from pydantic import BaseModel
from typing import Optional

class DepartmentCreate(BaseModel):
    name: str

class DepartmentUpdate(BaseModel):
    name: Optional[str] = None

class DepartmentOut(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True
