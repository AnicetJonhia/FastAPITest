from fastapi import FastAPI
from app.db.session import engine, SessionLocal
from app.models.base import Base
from app.api import auth, users, departments, documents, checklists
from app.core.config import ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_USERNAME
from app.crud.user_crud import create_superadmin, get_user_by_email

# create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="HelloFmap - Onboarding Platform (MVP)")

# include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(departments.router)
app.include_router(documents.router)
app.include_router(checklists.router)

@app.on_event("startup")
def startup_event():
    # Bootstrap superadmin if env vars set and not exist
    if ADMIN_EMAIL and ADMIN_PASSWORD:
        db = SessionLocal()
        try:
            existing = get_user_by_email(db, ADMIN_EMAIL)
            if not existing:
                create_superadmin(db, email=ADMIN_EMAIL, password=ADMIN_PASSWORD, username=ADMIN_USERNAME)
                print("SuperAdmin created:", ADMIN_EMAIL)
            else:
                print("SuperAdmin exists:", ADMIN_EMAIL)
        finally:
            db.close()

@app.get("/")
def root():
    return {"message": "HelloFmap API is running"}
