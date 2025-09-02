from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from app.models.base import Base
import enum

class RoleEnum(str, enum.Enum):
    SUPERADMIN = "SUPERADMIN"
    RH = "RH"
    DEPT = "DEPT"
    EMPLOYEE = "EMPLOYEE"
    MANAGER = "MANAGER"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)

