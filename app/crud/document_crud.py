from sqlalchemy.orm import Session
from app.models.document import Document
from app.schemas.document import DocumentCreate




def create_document(db: Session, doc_in: DocumentCreate) -> Document:
    doc = Document(title=doc_in.title, content=doc_in.content, department_id=doc_in.department_id)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc




def list_documents(db: Session, department_id: int = None, skip: int = 0, limit: int = 100):
    q = db.query(Document)
    if department_id is not None:
        q = q.filter(Document.department_id == department_id)
    return q.offset(skip).limit(limit).all()




def get_document(db: Session, doc_id: int):
    return db.query(Document).filter(Document.id == doc_id).first()