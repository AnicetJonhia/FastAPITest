# app/api/checklists.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.schemas.checklist import ChecklistCreate, ChecklistOut, ChecklistUpdate
from app.crud.checklist_crud import (
    create_checklist_item,
    list_checklist_items_for_user,
    list_department_template,
    mark_item_completed,
    get_checklist_item,
    list_all_checklist_items,
    update_checklist_item,
    delete_checklist_item,
)
from app.api.dependencies import get_current_user, require_role
from app.crud.user_crud import get_user_by_id
from app.services.onboarding import assign_onboarding_for_user

router = APIRouter(prefix="/checklists", tags=["checklists"])


# Create checklist item (assign to user or template if user_id is None)
@router.post("/", response_model=ChecklistOut, status_code=status.HTTP_201_CREATED)
def create_item(
    item_in: ChecklistCreate,
    db: Session = Depends(get_db),
    auth_user=Depends(require_role(["SUPERADMIN", "RH", "DEPT", "MANAGER"])),
):
    if item_in.user_id:
        target_user = get_user_by_id(db, item_in.user_id)
        if not target_user:
            raise HTTPException(status_code=404, detail="Target user not found")

        # DEPT/MANAGER => doivent appartenir au même département
        if auth_user.role in ("DEPT", "MANAGER") and auth_user.department_id != target_user.department_id:
            raise HTTPException(status_code=403, detail="Not allowed to assign to another department")

    item = create_checklist_item(db, item_in)
    return item


# Create template (user_id must be None)
@router.post("/template", response_model=ChecklistOut, status_code=status.HTTP_201_CREATED)
def create_template(
    item_in: ChecklistCreate,
    db: Session = Depends(get_db),
    auth_user=Depends(require_role(["SUPERADMIN", "RH", "DEPT"])),
):
    if item_in.user_id is not None:
        raise HTTPException(status_code=400, detail="Template must not have user_id")
    return create_checklist_item(db, item_in)


# List items
@router.get("/", response_model=List[ChecklistOut])
def list_items(
    user_id: Optional[int] = None,
    department_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    auth_user=Depends(get_current_user),
):
    if user_id:
        target_user = get_user_by_id(db, user_id)
        if not target_user:
            raise HTTPException(status_code=404, detail="Target user not found")

        # droits : owner, SUPERADMIN, RH, DEPT(manager du même dept)
        if auth_user.id == user_id:
            return list_checklist_items_for_user(db, user_id)

        if auth_user.role in ("SUPERADMIN", "RH"):
            return list_checklist_items_for_user(db, user_id)

        if auth_user.role in ("DEPT", "MANAGER") and auth_user.department_id == target_user.department_id:
            return list_checklist_items_for_user(db, user_id)

        raise HTTPException(status_code=403, detail="Not allowed to view these items")

    if department_id is not None:
        # DEPT/MANAGER ne peuvent que leur propre département
        if auth_user.role in ("DEPT", "MANAGER") and auth_user.department_id != department_id:
            raise HTTPException(status_code=403, detail="Not allowed to view templates of another department")
        return list_department_template(db, department_id)

    # listing global
    if auth_user.role in ("SUPERADMIN", "RH"):
        return list_all_checklist_items(db, skip=skip, limit=limit)

    raise HTTPException(status_code=403, detail="Not allowed to list all checklists")


# Get my checklist
@router.get("/me", response_model=List[ChecklistOut])
def my_checklist(db: Session = Depends(get_db), auth_user=Depends(get_current_user)):
    return list_checklist_items_for_user(db, auth_user.id)


# Get single item
@router.get("/{item_id}", response_model=ChecklistOut)
def get_item(item_id: int, db: Session = Depends(get_db), auth_user=Depends(get_current_user)):
    item = get_checklist_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if item.user_id == auth_user.id:
        return item

    target_user = get_user_by_id(db, item.user_id) if item.user_id else None

    if auth_user.role in ("SUPERADMIN", "RH"):
        return item

    if auth_user.role in ("DEPT", "MANAGER") and target_user and auth_user.department_id == target_user.department_id:
        return item

    raise HTTPException(status_code=403, detail="Not allowed")


# Update item
@router.put("/{item_id}", response_model=ChecklistOut)
def update_item(item_id: int, payload: ChecklistUpdate, db: Session = Depends(get_db), auth_user=Depends(get_current_user)):
    item = get_checklist_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    target_user = get_user_by_id(db, item.user_id) if item.user_id else None

    allowed = False
    if auth_user.role in ("SUPERADMIN", "RH"):
        allowed = True
    if auth_user.role in ("DEPT", "MANAGER") and target_user and auth_user.department_id == target_user.department_id:
        allowed = True
    if auth_user.id == item.user_id:
        allowed = True

    if not allowed:
        raise HTTPException(status_code=403, detail="Not allowed to update this item")

    updated = update_checklist_item(db, item_id, payload.dict())
    if not updated:
        raise HTTPException(status_code=500, detail="Unable to update item")
    return updated


# Mark complete
@router.post("/{item_id}/complete", response_model=ChecklistOut)
def complete_item(item_id: int, db: Session = Depends(get_db), auth_user=Depends(get_current_user)):
    item = get_checklist_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if item.user_id == auth_user.id:
        return mark_item_completed(db, item_id)

    target_user = get_user_by_id(db, item.user_id) if item.user_id else None

    if auth_user.role in ("SUPERADMIN", "RH"):
        return mark_item_completed(db, item_id)

    if auth_user.role == "MANAGER" and target_user and auth_user.department_id == target_user.department_id:
        return mark_item_completed(db, item_id)

    raise HTTPException(status_code=403, detail="Not allowed to complete this item")


# Delete item
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db), auth_user=Depends(require_role(["SUPERADMIN", "RH"]))):
    item = get_checklist_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    deleted = delete_checklist_item(db, item_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="Unable to delete item")
    return None


# Assign templates to a user
@router.post("/assign/{user_id}", response_model=List[ChecklistOut], status_code=status.HTTP_201_CREATED)
def assign_templates_to_user(
    user_id: int,
    db: Session = Depends(get_db),
    auth_user=Depends(require_role(["SUPERADMIN", "RH", "DEPT", "MANAGER"])),
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Target user not found")

    if auth_user.role in ("DEPT", "MANAGER") and auth_user.department_id != user.department_id:
        raise HTTPException(status_code=403, detail="Cannot assign templates to another department")

    created, docs = assign_onboarding_for_user(db, user)
    return created
