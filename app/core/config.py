import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hellofmap.db")
SECRET_KEY = os.getenv("SECRET_KEY", "change_this_secret_for_dev_only")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24