# app/api/documents.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
import os
import shutil

from app.db.session import get_db
from app.crud.document_crud import (
    create_document_record,
    list_documents,
    get_document,
    update_document_record,
    delete_document_record,
)
from app.schemas.document import DocumentOut, DocumentUpdate
from app.api.dependencies import require_role, get_current_user
from app.services.file_storage import save_upload_file
from app.core.config import STORAGE_DIR

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def upload_document(
    title: str,
    department_id: Optional[int] = None,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    auth_user = Depends(require_role(["SUPERADMIN", "RH", "DEPT"])),
):
    """
    Upload a file and create a document record.
    - SUPERADMIN / RH: can upload for any department (or global if department_id=None)
    - DEPT: can only upload documents for their own department
    """
    # DEPTs can only create for their own department
    if getattr(auth_user, "role", None) == "DEPT":
        if department_id is None or auth_user.department_id != department_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Department admins can only upload files to their own department")

    # Save file to disk
    try:
        stored_name, path = save_upload_file(file)
    except Exception as exc:
        # possible I/O error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to save uploaded file: {exc}")

    # create DB record — if DB fails, remove file to avoid orphan files
    try:
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
    except Exception as exc:
        # cleanup saved file
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to create document record: {exc}")


@router.get("/", response_model=List[DocumentOut])
def get_docs(
    department_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    auth_user = Depends(get_current_user),
):
    """
    List documents visible to the current user:
      - SUPERADMIN / RH: all documents (optionally filtered by department_id)
      - Others: global documents (department_id IS NULL) + documents of the user's department
    Non-admins cannot request documents for other departments.
    """
    user_role = getattr(auth_user, "role", None)
    user_dept = getattr(auth_user, "department_id", None)

    if user_role in ("SUPERADMIN", "RH"):
        # full access, allow optional department filter
        return list_documents(db, department_id=department_id, skip=skip, limit=limit)

    # Non-admin: cannot ask for other departments explicitly
    if department_id is not None and department_id != user_dept:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Cannot access documents of other department")

    # return global (None) OR same department
    q = db.query  # just for typing clarity below
    docs = db.query  # not needed but keep clarity
    from app.models.document import Document  # local import to avoid circular issues
    docs = db.query(Document).filter(
        or_(Document.department_id == None, Document.department_id == user_dept)
    ).offset(skip).limit(limit).all()
    return docs


@router.get("/{doc_id}", response_model=DocumentOut)
def get_doc(
    doc_id: int,
    db: Session = Depends(get_db),
    auth_user = Depends(get_current_user),
):
    doc = get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # permission: if departmental document, enforce dept match unless admin/RH
    user_role = getattr(auth_user, "role", None)
    if doc.department_id is not None and user_role not in ("SUPERADMIN", "RH"):
        if auth_user.department_id != doc.department_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access to this document")

    return doc


@router.get("/{doc_id}/download")
def download_doc(
    doc_id: int,
    db: Session = Depends(get_db),
    auth_user = Depends(get_current_user),
):
    doc = get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    user_role = getattr(auth_user, "role", None)
    if doc.department_id is not None and user_role not in ("SUPERADMIN", "RH"):
        if auth_user.department_id != doc.department_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access to this document")

    if not doc.path or not os.path.exists(doc.path):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="File missing on server")

    return FileResponse(path=doc.path, filename=doc.original_filename, media_type=doc.content_type)


@router.put("/{doc_id}", response_model=DocumentOut)
def update_doc_metadata(
    doc_id: int,
    payload: DocumentUpdate,
    db: Session = Depends(get_db),
    auth_user = Depends(require_role(["SUPERADMIN", "RH", "DEPT"])),
):
    """
    Update document metadata (title, department). Permissions:
      - SUPERADMIN/RH: can change anything
      - DEPT: can modify documents of their own department only
    """
    doc = get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # DEPT can only update docs of their department
    if getattr(auth_user, "role", None) == "DEPT":
        if doc.department_id != auth_user.department_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Department admin can only update documents of their own department")

    updated = update_document_record(db, doc_id, title=payload.title, department_id=payload.department_id)
    if not updated:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to update document")
    return updated


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_doc(
    doc_id: int,
    db: Session = Depends(get_db),
    auth_user = Depends(require_role(["SUPERADMIN", "RH"])),
):
    """
    Delete document (metadata + file).
    Only SUPERADMIN and RH allowed (by default).
    """
    doc = get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # remove file from disk first (best-effort)
    try:
        if doc.path and os.path.exists(doc.path):
            os.remove(doc.path)
    except Exception:
        # log in real app
        pass

    deleted = delete_document_record(db, doc_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to delete document")

    return None
