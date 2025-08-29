
from sqlalchemy.orm import Session
from app.models.department import Department
from app.schemas.department import DepartmentCreate, DepartmentUpdate
from typing import List, Optional

def create_department(db: Session, dept_in: DepartmentCreate) -> Department:

    existing = db.query(Department).filter(Department.name == dept_in.name).first()
    if existing:
        return existing
    dept = Department(name=dept_in.name)
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept

def get_department(db: Session, dept_id: int) -> Optional[Department]:
    return db.query(Department).filter(Department.id == dept_id).first()

def list_departments(db: Session, skip: int = 0, limit: int = 100) -> List[Department]:
    return db.query(Department).offset(skip).limit(limit).all()

def update_department(db: Session, dept_id: int, dept_in: DepartmentUpdate) -> Optional[Department]:
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        return None
    if dept_in.name is not None:
        dept.name = dept_in.name
    db.commit()
    db.refresh(dept)
    return dept

def delete_department(db: Session, dept_id: int) -> Optional[Department]:
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        return None
    db.delete(dept)
    db.commit()
    return dept
