
from app.models.user import User, RoleEnum
from app.schemas.user import UserCreate

from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserUpdate
from app.core.security import hash_password

def create_user(db: Session, user_in: UserCreate) -> User:
    user = User(
        username=user_in.username,
        full_name=user_in.full_name,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        role=user_in.role,
        department_id=user_in.department_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_superadmin(db: Session, email: str, password: str, username: str = "SuperAdmin"):
    # convenience helper to bootstrap a superadmin
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user
    user = User(
        username=username,
        full_name="",
        email=email,
        hashed_password=hash_password(password),
        role=RoleEnum.SUPERADMIN,
        department_id=None
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def list_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()



def update_user(db: Session, user: User, user_in: UserUpdate) -> User:
    if user_in.username:
        user.username = user_in.username
    if user_in.full_name:
        user.full_name = user_in.full_name
    if user_in.email:
        user.email = user_in.email
    if user_in.password:
        user.hashed_password = hash_password(user_in.password)
    if user_in.role:
        user.role = user_in.role

    # Gestion du department_id
    if user_in.department_id is not None:
        # Vérifier si le département existe
        from app.crud.department_crud import get_department
        dept = get_department(db, user_in.department_id)
        if dept:
            user.department_id = dept.id
        else:
            user.department_id = None

    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user: User):
    db.delete(user)
    db.commit()
