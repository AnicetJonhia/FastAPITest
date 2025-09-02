from fastapi import FastAPI
from app.db.session import engine, SessionLocal
from app.models.base import Base
from app.api import auth, users, departments, documents, checklists
from app.core.config import settings
from app.crud.user_crud import create_superadmin, get_user_by_email

# create tables
Base.metadata.create_all(bind=engine)




def include_routers_with_prefix(app: FastAPI, routers: list, prefix: str = "/api"):
    for router in routers:
        app.include_router(router, prefix=prefix)


app = FastAPI(title="HelloFmap - Onboarding Platform (MVP)")
routers = [auth.router, users.router, departments.router, documents.router, checklists.router]

include_routers_with_prefix(app, routers)

@app.on_event("startup")
def startup_event():
    # Bootstrap superadmin if env vars set and not exist
    if settings.ADMIN_EMAIL and settings.ADMIN_PASSWORD:
        db = SessionLocal()
        try:
            existing = get_user_by_email(db, settings.ADMIN_EMAIL)
            if not existing:
                create_superadmin(db, email=settings.ADMIN_EMAIL, password=settings.ADMIN_PASSWORD, username=settings.ADMIN_USERNAME)
                print("SuperAdmin created:", settings.ADMIN_EMAIL)
            else:
                print("SuperAdmin exists:", settings.ADMIN_EMAIL)
        finally:
            db.close()

@app.get("/")
def root():
    return {"message": "HelloFmap API is running"}
