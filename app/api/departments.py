
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.department import DepartmentCreate, DepartmentOut, DepartmentUpdate
from app.crud.department_crud import (
    create_department,
    list_departments,
    get_department,
    update_department,
    delete_department,
)
from app.api.dependencies import require_role

router = APIRouter(prefix="/departments", tags=["departments"])


@router.post("/", response_model=DepartmentOut, status_code=status.HTTP_201_CREATED)
def create_dept(
    dept_in: DepartmentCreate,
    db: Session = Depends(get_db),
    auth_user=Depends(require_role(["SUPERADMIN", "RH"])),
):
    return create_department(db, dept_in)


@router.get("/", response_model=List[DepartmentOut])
def get_departments(
    db: Session = Depends(get_db),
    auth_user=Depends(require_role(["SUPERADMIN", "RH", "DEPT", "MANAGER"])),
):
    return list_departments(db)


@router.get("/{dept_id}", response_model=DepartmentOut)
def get_dept(
    dept_id: int,
    db: Session = Depends(get_db),
    auth_user=Depends(require_role(["SUPERADMIN", "RH", "DEPT", "MANAGER"])),
):
    dept = get_department(db, dept_id)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    return dept


@router.put("/{dept_id}", response_model=DepartmentOut)
def update_dept(
    dept_id: int,
    dept_in: DepartmentUpdate,
    db: Session = Depends(get_db),
    auth_user=Depends(require_role(["SUPERADMIN", "RH"])),
):
    dept = update_department(db, dept_id, dept_in)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    return dept


@router.delete("/{dept_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dept(
    dept_id: int,
    db: Session = Depends(get_db),
    auth_user=Depends(require_role(["SUPERADMIN", "RH"])),
):
    dept = delete_department(db, dept_id)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    return None
