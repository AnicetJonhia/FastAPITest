from sqlalchemy.orm import Session
from app.models.user import User, RoleEnum
from app.schemas.user import UserCreate
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
