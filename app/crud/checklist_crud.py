from sqlalchemy.orm import Session
from app.models.checklist import ChecklistItem
from app.schemas.checklist import ChecklistCreate

def create_checklist_item(db: Session, item_in: ChecklistCreate) -> ChecklistItem:
    item = ChecklistItem(title=item_in.title, department_id=item_in.department_id, user_id=item_in.user_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def list_checklist_items_for_user(db: Session, user_id: int):
    return db.query(ChecklistItem).filter(ChecklistItem.user_id == user_id).all()

def list_department_template(db: Session, department_id: int):
    return db.query(ChecklistItem).filter(ChecklistItem.department_id == department_id, ChecklistItem.user_id == None).all()

def mark_item_completed(db: Session, item_id: int):
    item = db.query(ChecklistItem).filter(ChecklistItem.id == item_id).first()
    if item:
        item.completed = True
        db.commit()
        db.refresh(item)
    return item
