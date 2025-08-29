# app/schemas/checklist.py
from pydantic import BaseModel
from typing import Optional

class ChecklistCreate(BaseModel):
    title: str
    department_id: Optional[int] = None
    user_id: Optional[int] = None

class ChecklistUpdate(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None
    department_id: Optional[int] = None
    user_id: Optional[int] = None

class ChecklistOut(BaseModel):
    id: int
    title: str
    completed: bool
    user_id: Optional[int]
    department_id: Optional[int]

    class Config:
        orm_mode = True
