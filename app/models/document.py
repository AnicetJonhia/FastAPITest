from sqlalchemy import Column, Integer, String, ForeignKey
from app.models.base import Base

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)  # Null = RH Global
