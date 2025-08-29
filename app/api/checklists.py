from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.checklist import ChecklistCreate, ChecklistOut
from app.crud.checklist_crud import create_checklist_item, list_checklist_items_for_user, mark_item_completed
from app.api.dependencies import get_current_user, require_role


router = APIRouter()


@router.post("/", response_model=ChecklistOut)
def create_item(item_in: ChecklistCreate, db: Session = Depends(get_db), auth_user=Depends(require_role(["RH", "DEPT"]))):
    return create_checklist_item(db, item_in)


@router.get("/me", response_model=List[ChecklistOut])
def my_checklist(db: Session = Depends(get_db), auth_user=Depends(get_current_user)):
    return list_checklist_items_for_user(db, auth_user.id)


@router.post("/{item_id}/complete", response_model=ChecklistOut)
def complete_item(item_id: int, db: Session = Depends(get_db), auth_user=Depends(get_current_user)):
    item = mark_item_completed(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item