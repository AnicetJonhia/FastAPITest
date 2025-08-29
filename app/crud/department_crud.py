from sqlalchemy.orm import Session
from app.models.department import Department
from app.schemas.department import DepartmentCreate

def create_department(db: Session, dept_in: DepartmentCreate) -> Department:
    dept = Department(name=dept_in.name)
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept

def get_department(db: Session, dept_id: int):
    return db.query(Department).filter(Department.id == dept_id).first()


def list_departments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Department).offset(skip).limit(limit).all()