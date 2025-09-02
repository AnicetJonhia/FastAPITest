from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError, ExpiredSignatureError
from app.core.config import settings

# Gestion du hashage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ----------------------------
#      ACCESS TOKEN
# ----------------------------
def create_access_token(user_id: int, role: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crée un token JWT pour l'authentification.
    Payload : {'sub': user_id, 'role': role, 'exp': ...}
    """
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {"sub": str(user_id), "role": role, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Décode et valide un access token
    Retourne le payload {'sub': user_id, 'role': role, 'exp': ...} ou None si invalide/expiré
    """
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except ExpiredSignatureError:
        return None
    except JWTError:
        return None


# ----------------------------
#      RESET PASSWORD TOKEN
# ----------------------------
def create_reset_token(email: str) -> str:
    """
    Crée un token JWT pour la réinitialisation du mot de passe.
    Payload : {'sub': email, 'exp': ...}
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.FORGET_PASSWORD_LINK_EXPIRE_MINUTES)
    payload = {"sub": email, "exp": expire}
    return jwt.encode(payload, settings.FORGET_PASSWORD_SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_reset_token(token: str) -> Optional[str]:
    """
    Décode un reset token et retourne l'email s'il est valide
    """
    try:
        payload = jwt.decode(token, settings.FORGET_PASSWORD_SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload.get("sub")
    except ExpiredSignatureError:
        return None
    except JWTError:
        return None
