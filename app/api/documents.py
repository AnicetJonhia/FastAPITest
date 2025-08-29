from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.schemas.document import DocumentCreate, DocumentOut
from app.crud.document_crud import create_document, list_documents, get_document
from app.api.dependencies import require_role, get_current_user


router = APIRouter()


@router.post("/", response_model=DocumentOut)
def create_doc(doc_in: DocumentCreate, db: Session = Depends(get_db), auth_user=Depends(require_role(["RH", "DEPT"]))):
    return create_document(db, doc_in)


@router.get("/", response_model=List[DocumentOut])
def get_docs(department_id: Optional[int] = None, db: Session = Depends(get_db), auth_user=Depends(get_current_user)):
    return list_documents(db, department_id=department_id)


@router.get("/{doc_id}", response_model=DocumentOut)
def get_doc(doc_id: int, db: Session = Depends(get_db), auth_user=Depends(get_current_user)):
    doc = get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc