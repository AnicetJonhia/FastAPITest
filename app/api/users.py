from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.user import UserCreate, UserOut
from app.crud.user_crud import create_user, list_users, get_user_by_id
from app.api.dependencies import get_current_user, require_role
from app.services.onboarding import assign_onboarding_for_user
from app.services.email_service import send_welcome_email


router = APIRouter()


@router.post("/", response_model=UserOut)
def create_new_user(user_in: UserCreate, db: Session = Depends(get_db), auth_user=Depends(require_role(["RH"]))):
    # Only RH can create users (MVP)
    user = create_user(db, user_in)
    # Assign onboarding
    items, docs = assign_onboarding_for_user(db, user)
    # Send email stub
    send_welcome_email(user.email, user.full_name or user.username)
    return user


@router.get("/", response_model=List[UserOut])
def get_users(db: Session = Depends(get_db), auth_user=Depends(require_role(["RH", "MANAGER"]))):
    return list_users(db)


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), auth_user=Depends(get_current_user)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user