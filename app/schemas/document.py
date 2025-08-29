from pydantic import BaseModel
from typing import Optional

class DocumentOut(BaseModel):
    id: int
    title: str
    original_filename: str
    content_type: Optional[str]
    department_id: Optional[int]
    uploaded_by: Optional[int]

    class Config:
        orm_mode = True
