from sqlalchemy.orm import Session
from app.models.document import Document
from typing import Optional

def create_document_record(db: Session, title: str, stored_filename: str, original_filename: str,
                           content_type: str, path: str, uploaded_by: int = None, department_id: Optional[int] = None):
    doc = Document(
        title=title,
        stored_filename=stored_filename,
        original_filename=original_filename,
        content_type=content_type,
        path=path,
        uploaded_by=uploaded_by,
        department_id=department_id
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def get_document(db: Session, doc_id: int):
    return db.query(Document).filter(Document.id == doc_id).first()

def list_documents(db: Session, department_id: int = None, skip: int = 0, limit: int = 100):
    q = db.query(Document)
    if department_id is not None:
        q = q.filter(Document.department_id == department_id)
    return q.offset(skip).limit(limit).all()
