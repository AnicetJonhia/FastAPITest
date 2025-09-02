
from sqlalchemy.orm import Session
from app.models.checklist import ChecklistItem
from app.schemas.checklist import ChecklistCreate
from typing import List, Optional

def create_checklist_item(db: Session, item_in: ChecklistCreate) -> ChecklistItem:
    item = ChecklistItem(
        title=item_in.title,
        department_id=item_in.department_id,
        user_id=item_in.user_id
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def get_checklist_item(db: Session, item_id: int) -> Optional[ChecklistItem]:
    return db.query(ChecklistItem).filter(ChecklistItem.id == item_id).first()

def list_checklist_items_for_user(db: Session, user_id: int) -> List[ChecklistItem]:
    return db.query(ChecklistItem).filter(ChecklistItem.user_id == user_id).all()

def list_all_checklist_items(db: Session, skip: int = 0, limit: int = 100) -> List[ChecklistItem]:
    return db.query(ChecklistItem).offset(skip).limit(limit).all()

def list_department_template(db: Session, department_id: Optional[int]) -> List[ChecklistItem]:
    # Templates defined as items with user_id == None
    q = db.query(ChecklistItem).filter(ChecklistItem.user_id == None)
    if department_id is None:
        q = q.filter(ChecklistItem.department_id == None)
    else:
        q = q.filter(ChecklistItem.department_id == department_id)
    return q.all()

def mark_item_completed(db: Session, item_id: int) -> Optional[ChecklistItem]:
    item = get_checklist_item(db, item_id)
    if item:
        item.completed = True
        db.commit()
        db.refresh(item)
    return item

def update_checklist_item(db: Session, item_id: int, payload: dict) -> Optional[ChecklistItem]:
    item = get_checklist_item(db, item_id)
    if not item:
        return None

    # applique uniquement les champs envoyés
    for field, value in payload.items():
        if value is not None:  # ne change que si une valeur est donnée
            setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


def delete_checklist_item(db: Session, item_id: int) -> Optional[ChecklistItem]:
    item = get_checklist_item(db, item_id)
    if not item:
        return None
    db.delete(item)
    db.commit()
    return item
