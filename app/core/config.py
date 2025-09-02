from dotenv import load_dotenv
import os
from pathlib import Path
from pydantic import BaseSettings, EmailStr

# Charge le .env manuellement si présent
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/hellofmap.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change_this_secret_for_dev_only")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60*24))

    STORAGE_DIR: str = os.getenv("STORAGE_DIR", os.path.join(BASE_DIR, "..", "storage"))

    ADMIN_EMAIL: EmailStr = os.getenv("ADMIN_EMAIL", None)
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", None)
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "SuperAdmin")

    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "localhost")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 25))
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "False").lower() == "true"
    SMTP_USER: str = os.getenv("SMTP_USER", None)
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", None)
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "no-reply@example.com")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Instancier les settings
settings = Settings()

# S'assurer que le dossier de stockage existe
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
