# app/api/checklists.py
from fastapi import APIRouter, Depends, HTTPException, status
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

router = APIRouter(prefix="/checklists", tags=["checklists"])

# Create checklist item (assign to user or create a template if user_id is None)
@router.post("/", response_model=ChecklistOut, status_code=status.HTTP_201_CREATED)
def create_item(
    item_in: ChecklistCreate,
    db: Session = Depends(get_db),
    auth_user = Depends(require_role(["SUPERADMIN", "RH", "DEPT"]))
):
    # If creating item assigned to user, optionally enforce that creator can assign to that department/user
    item = create_checklist_item(db, item_in)
    return item

# Create template (explicit endpoint) - template = user_id is None
@router.post("/template", response_model=ChecklistOut, status_code=status.HTTP_201_CREATED)
def create_template(
    item_in: ChecklistCreate,
    db: Session = Depends(get_db),
    auth_user = Depends(require_role(["SUPERADMIN", "RH", "DEPT"]))
):
    if item_in.user_id is not None:
        raise HTTPException(status_code=400, detail="Template must have no user_id")
    item = create_checklist_item(db, item_in)
    return item

# List items - supports filters
@router.get("/", response_model=List[ChecklistOut])
def list_items(
    user_id: Optional[int] = None,
    department_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    auth_user = Depends(get_current_user)
):
    # If user_id specified must be admin or self
    if user_id:
        if auth_user.role not in ("SUPERADMIN", "RH", "MANAGER") and auth_user.id != user_id:
            raise HTTPException(status_code=403, detail="Not allowed to view these items")
        return list_checklist_items_for_user(db, user_id)
    # department template listing
    if department_id is not None:
        return list_department_template(db, department_id)
    return list_all_checklist_items(db, skip=skip, limit=limit)

# Get current user's checklist
@router.get("/me", response_model=List[ChecklistOut])
def my_checklist(db: Session = Depends(get_db), auth_user = Depends(get_current_user)):
    return list_checklist_items_for_user(db, auth_user.id)

# Get single item
@router.get("/{item_id}", response_model=ChecklistOut)
def get_item(item_id: int, db: Session = Depends(get_db), auth_user = Depends(get_current_user)):
    item = get_checklist_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    # permission: owner or admin/HR/manager
    if item.user_id is not None and auth_user.id != item.user_id and auth_user.role not in ("SUPERADMIN", "RH", "MANAGER"):
        raise HTTPException(status_code=403, detail="Not allowed")
    return item

# Update item
@router.put("/{item_id}", response_model=ChecklistOut)
def update_item(item_id: int, payload: ChecklistUpdate, db: Session = Depends(get_db), auth_user = Depends(get_current_user)):
    item = get_checklist_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # permission: SUPERADMIN/RH/DEPT can update any; owner can update his own; manager can update completed state maybe
    allowed = False
    if auth_user.role in ("SUPERADMIN", "RH", "DEPT"):
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
def complete_item(item_id: int, db: Session = Depends(get_db), auth_user = Depends(get_current_user)):
    item = get_checklist_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    # permission: owner or manager or RH or SUPERADMIN
    if auth_user.id != item.user_id and auth_user.role not in ("SUPERADMIN", "RH", "MANAGER"):
        raise HTTPException(status_code=403, detail="Not allowed to complete this item")
    updated = mark_item_completed(db, item_id)
    return updated

# Delete item
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db), auth_user = Depends(require_role(["SUPERADMIN", "RH"]))):
    item = get_checklist_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    deleted = delete_checklist_item(db, item_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="Unable to delete item")
    return None
