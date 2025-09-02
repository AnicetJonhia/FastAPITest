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


# ✅ CREATE (seulement SUPERADMIN)
@router.post("/", response_model=UserOut)
def create_new_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    auth_user=Depends(require_role(["SUPERADMIN"])),
):
    user = create_user(db, user_in)
    items, docs = assign_onboarding_for_user(db, user)
    send_welcome_email(user.email, user.full_name or user.username)
    return user


# ✅ READ ALL
@router.get("/", response_model=List[UserOut])
def get_users(
    db: Session = Depends(get_db),
    auth_user=Depends(require_role(["SUPERADMIN", "RH", "MANAGER", "DEPT"])),
):
    all_users = list_users(db)

    # MANAGER / DEPT → seulement leur département
    if auth_user.role in ("MANAGER", "DEPT"):
        return [u for u in all_users if u.department_id == auth_user.department_id]

    return all_users


# ✅ READ ONE
@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    auth_user=Depends(get_current_user),
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # User normal → seulement soi-même
    if auth_user.role not in ["SUPERADMIN", "RH", "MANAGER", "DEPT"] and auth_user.id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed to access this user")

    # Manager/Dept → seulement leur département
    if auth_user.role in ("MANAGER", "DEPT") and auth_user.department_id != user.department_id:
        raise HTTPException(status_code=403, detail="Cannot access user from another department")

    return user


# ✅ UPDATE
@router.put("/{user_id}", response_model=UserOut)
def update_user_route(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    auth_user=Depends(get_current_user),
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Permissions
    if auth_user.role == "SUPERADMIN":
        pass
    elif auth_user.role == "RH" and user.role != "SUPERADMIN":
        pass
    elif auth_user.role in ("MANAGER", "DEPT") and user.department_id == auth_user.department_id:
        pass  # limité à leur département

    else:
        raise HTTPException(status_code=403, detail="Not allowed to update this user")

    # 🔹 Conserver le department_id avant mise à jour
    old_department_id = user.department_id

    # Mise à jour du user
    updated_user = update_user(db, user, user_in)

    # 🔄 Réassigner l'onboarding uniquement si le department_id a changé
    if old_department_id != updated_user.department_id:
        items , docs = assign_onboarding_for_user(db, updated_user)

    return updated_user



# ✅ DELETE (seulement SUPERADMIN)
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_route(
    user_id: int,
    db: Session = Depends(get_db),
    auth_user=Depends(require_role(["SUPERADMIN"])),
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    delete_user(db, user)
    return None
