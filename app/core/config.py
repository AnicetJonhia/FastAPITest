from dotenv import load_dotenv
import os
from pathlib import Path
from pydantic import BaseSettings, EmailStr
from fastapi_mail import ConnectionConfig

# Charge le .env manuellement si présent
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / "templates" / "emails"
TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/hellofmap.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change_this_secret_for_dev_only")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))

    STORAGE_DIR: str = os.getenv("STORAGE_DIR", os.path.join(BASE_DIR, "..", "storage"))

    ADMIN_EMAIL: EmailStr = os.getenv("ADMIN_EMAIL", None)
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", None)
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "SuperAdmin")

    FORGET_PASSWORD_LINK_EXPIRE_MINUTES: int = os.getenv("FORGET_PASSWORD_LINK_EXPIRE_MINUTES", 60)
    FORGET_PASSWORD_SECRET_KEY: str = os.getenv("FORGET_PASSWORD_SECRET_KEY", "secret_key_for_dev_only")

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

    @property
    def mail_conf(self) -> ConnectionConfig:
        template_path = Path(BASE_DIR) / "templates" / "emails"
        if not template_path.exists():
            template_path.mkdir(parents=True, exist_ok=True)

        use_credentials = bool(self.SMTP_USER and self.SMTP_PASSWORD)

        return ConnectionConfig(
            MAIL_USERNAME=self.SMTP_USER if use_credentials else "",
            MAIL_PASSWORD=self.SMTP_PASSWORD if use_credentials else "",
            MAIL_FROM=self.EMAIL_FROM,
            MAIL_PORT=self.SMTP_PORT,
            MAIL_SERVER=self.SMTP_SERVER,
            MAIL_TLS=self.SMTP_TLS,
            MAIL_SSL=not self.SMTP_TLS,
            USE_CREDENTIALS=use_credentials,
            TEMPLATE_FOLDER=str(TEMPLATE_DIR),
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Instancier les settings
settings = Settings()

# S'assurer que le dossier de stockage existe
os.makedirs(settings.STORAGE_DIR, exist_ok=True)

