from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os

from app.db.session import get_db
from app.crud.document_crud import create_document_record, list_documents, get_document
from app.api.dependencies import require_role, get_current_user
from app.schemas.document import DocumentOut
from app.services.file_storage import save_upload_file
from app.core.config import STORAGE_DIR

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/", response_model=DocumentOut)
def upload_document(title: str, department_id: Optional[int] = None,
                    file: UploadFile = File(...),
                    db: Session = Depends(get_db),
                    auth_user = Depends(require_role(["SUPERADMIN", "RH", "DEPT"]))):
    stored_name, path = save_upload_file(file)
    doc = create_document_record(
        db=db,
        title=title,
        stored_filename=stored_name,
        original_filename=file.filename,
        content_type=file.content_type,
        path=path,
        uploaded_by=auth_user.id,
        department_id=department_id
    )
    return doc

@router.get("/", response_model=List[DocumentOut])
def get_docs(department_id: Optional[int] = None, db: Session = Depends(get_db), auth_user = Depends(get_current_user)):
    return list_documents(db, department_id=department_id)

@router.get("/{doc_id}/download")
def download_doc(doc_id: int, db: Session = Depends(get_db), auth_user = Depends(get_current_user)):
    doc = get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    # check permission: if doc.department_id not None ensure user's department matches or is admin
    if doc.department_id is not None and getattr(auth_user, "role", None) not in ("SUPERADMIN", "RH"):
        if auth_user.department_id != doc.department_id:
            raise HTTPException(status_code=403, detail="No access to this document")
    if not os.path.exists(doc.path):
        raise HTTPException(status_code=500, detail="File missing on server")
    return FileResponse(path=doc.path, filename=doc.original_filename, media_type=doc.content_type)
