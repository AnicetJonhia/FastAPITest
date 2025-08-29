# app/schemas/document.py
from pydantic import BaseModel
from typing import Optional

class DocumentCreate(BaseModel):
    title: str
    department_id: Optional[int] = None

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    department_id: Optional[int] = None

class DocumentOut(BaseModel):
    id: int
    title: str
    original_filename: str
    content_type: Optional[str]
    department_id: Optional[int]
    uploaded_by: Optional[int]

    class Config:
        orm_mode = True
