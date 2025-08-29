from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode_access_token
from app.crud.user_crud import get_user_by_email, get_user_by_id
from app.schemas.user import TokenPayload


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = decode_access_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        role = payload.get("role")
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(db, email)
    if user is None:
        raise credentials_exception
    return user




def require_role(required_roles: list):
    def role_checker(user = Depends(get_current_user)):
        if user.role.value not in required_roles and user.role not in required_roles:
            raise HTTPException(status_code=403, detail="Operation not permitted")
        return user
    return role_checker