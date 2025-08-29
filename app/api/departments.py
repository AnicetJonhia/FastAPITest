from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.department import DepartmentCreate, DepartmentOut
from app.crud.department_crud import create_department, list_departments
from app.api.dependencies import require_role

router = APIRouter(prefix="/departments", tags=["departments"])

@router.post("/", response_model=DepartmentOut)
def create_dept(dept_in: DepartmentCreate, db: Session = Depends(get_db), auth_user=Depends(require_role(["SUPERADMIN","RH"]))):
    return create_department(db, dept_in)

@router.get("/", response_model=List[DepartmentOut])
def get_departments(db: Session = Depends(get_db), auth_user=Depends(require_role(["SUPERADMIN","RH","DEPT","MANAGER"]))):
    return list_departments(db)
