from sqlalchemy.orm import Session
from app.crud.checklist_crud import create_checklist_item, list_department_template
from app.crud.document_crud import list_documents

def assign_onboarding_for_user(db: Session, user):
    global_templates = list_department_template(db, department_id=None)
    dept_templates = []
    if user.department_id:
        dept_templates = list_department_template(db, department_id=user.department_id)

    created = []
    for t in global_templates + dept_templates:
        new_item = create_checklist_item(db, type('X', (), {
            'title': t.title,
            'department_id': t.department_id,
            'user_id': user.id
        })())
        created.append(new_item)

    docs = list_documents(db, department_id=user.department_id)
    return created, docs
