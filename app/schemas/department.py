from pydantic import BaseModel

class DepartmentCreate(BaseModel):
    name: str

class DepartmentOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
