from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.user import UserCreate, UserOut, UserUpdate
from app.crud.user_crud import create_user, list_users, get_user_by_id, update_user, delete_user
from app.api.dependencies import get_current_user, require_role
from app.services.onboarding import assign_onboarding_for_user
from app.services.email_service import send_welcome_email

router = APIRouter(prefix="/users", tags=["users"])


# ✅ CREATE
@router.post("/", response_model=UserOut)
def create_new_user(
        user_in: UserCreate,
        db: Session = Depends(get_db),
        auth_user=Depends(require_role(["SUPERADMIN"]))
):
    user = create_user(db, user_in)
    items, docs = assign_onboarding_for_user(db, user)
    send_welcome_email(user.email, user.full_name or user.username)
    return user


# ✅ READ ALL
@router.get("/", response_model=List[UserOut])
def get_users(
        db: Session = Depends(get_db),
        auth_user=Depends(require_role(["SUPERADMIN", "RH", "MANAGER"]))
):
    return list_users(db)


# ✅ READ ONE
@router.get("/{user_id}", response_model=UserOut)
def get_user(
        user_id: int,
        db: Session = Depends(get_db),
        auth_user=Depends(get_current_user)
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Restriction : un utilisateur normal ne peut voir que son profil
    if auth_user.role not in ["SUPERADMIN", "RH", "MANAGER"] and auth_user.id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed to access this user")

    return user


# ✅ UPDATE
@router.put("/{user_id}", response_model=UserOut)
def update_user_route(
        user_id: int,
        user_in: UserUpdate,
        db: Session = Depends(get_db),
        auth_user=Depends(get_current_user)
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Permissions :
    if auth_user.role == "SUPERADMIN":
        pass  # full access
    elif auth_user.role == "RH" and user.role not in ["SUPERADMIN"]:
        pass  # RH peut modifier tout sauf les superadmins
    elif auth_user.id == user.id:
        pass  # un user peut modifier son propre profil
    else:
        raise HTTPException(status_code=403, detail="Not allowed to update this user")

    return update_user(db, user, user_in)


# ✅ DELETE
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_route(
        user_id: int,
        db: Session = Depends(get_db),
        auth_user=Depends(require_role(["SUPERADMIN"]))
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    delete_user(db, user)
    return None
