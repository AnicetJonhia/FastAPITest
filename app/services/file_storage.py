import os
import uuid
from fastapi import UploadFile
from app.core.config import settings

STORAGE_DIR =  settings.STORAGE_DIR
def save_upload_file(upload_file: UploadFile, subfolder: str = "") -> (str, str):
    """
    Save UploadFile to STORAGE_DIR[/subfolder] and return (stored_filename, path)
    stored_filename: unique name on disk
    path: absolute path where file was saved
    """
    ext = os.path.splitext(upload_file.filename)[1]
    stored_name = f"{uuid.uuid4().hex}{ext}"
    target_dir = STORAGE_DIR
    if subfolder:
        target_dir = os.path.join(STORAGE_DIR, subfolder)
        os.makedirs(target_dir, exist_ok=True)
    path = os.path.join(target_dir, stored_name)
    with open(path, "wb") as buffer:
        for chunk in upload_file.file:
            buffer.write(chunk)
    return stored_name, path
