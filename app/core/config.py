
from dotenv import load_dotenv

import os

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hellofmap.db")
SECRET_KEY = os.getenv("SECRET_KEY", "change_this_secret_for_dev_only")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24))
# File storage
STORAGE_DIR = os.getenv("STORAGE_DIR", os.path.join(BASE_DIR, "..", "storage"))
os.makedirs(STORAGE_DIR, exist_ok=True)

# Optional initial superadmin (to bootstrap)
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "SuperAdmin")
