from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from app.models.base import Base
import datetime

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    stored_filename = Column(String, nullable=False)  # filename on disk
    original_filename = Column(String, nullable=False)
    content_type = Column(String, nullable=True)
    path = Column(String, nullable=False)  # relative or absolute path where file is saved
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)  # None => global RH doc
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
