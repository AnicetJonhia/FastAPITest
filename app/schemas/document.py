from pydantic import BaseModel
from typing import Optional


class DocumentCreate(BaseModel):
    title: str
    content: Optional[str] = None
    department_id: Optional[int] = None


class DocumentOut(BaseModel):
    id: int
    title: str
    content: Optional[str]
    department_id: Optional[int]

    class Config:
        orm_mode = True