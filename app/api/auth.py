from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.db.session import get_db
from app.core.security import verify_password, create_access_token
from app.crud.user_crud import get_user_by_email
from app.schemas.user import Token
from app.models.user import User
from app.api.dependencies import get_current_user
from app.schemas.user import UserOut

router = APIRouter(prefix="/auth", tags=["auth"])

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day


@router.post("/token", response_model=Token)
def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    # d'abord essayer avec email
    user = get_user_by_email(db, form_data.username)

    # sinon essayer avec username
    if not user:
        user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        {"sub": user.email, "role": user.role.value},
        expires_delta=access_token_expires
    )
    return {"access_token": token, "token_type": "bearer"}




@router.get("/me", response_model=UserOut)
def read_me(current_user = Depends(get_current_user)):
    return current_user
