from fastapi import FastAPI
from app.db.session import engine
from app.models.base import Base
from app.api import auth, users, departments, documents, checklists


# Create DB tables
Base.metadata.create_all(bind=engine)


app = FastAPI(title="HelloFmap - Onboarding Platform (MVP)")


# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(departments.router, prefix="/departments", tags=["departments"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(checklists.router, prefix="/checklists", tags=["checklists"])


@app.get("/")
def root():
    return {"message": "HelloFmap API is running"}