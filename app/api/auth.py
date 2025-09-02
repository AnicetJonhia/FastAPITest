from datetime import timedelta

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.crud.user_crud import get_user_by_email
from app.api.dependencies import get_current_user
from app.services.email_service import send_reset_password_email
from app.core.security import (
    create_reset_token,
    decode_reset_token,
    hash_password,
    verify_password,
    create_access_token
)
from app.schemas.user import (
    Token,
    UserOut,
    ForgotPasswordRequest,
    ResetPasswordRequest
)

from app.core.config import settings

ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES or 1440


router = APIRouter(prefix="/auth", tags=["auth"])

# LOGIN / GET TOKEN
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
        user_id=user.id,  # passer l'ID de l'utilisateur
        role=user.role,  # passer le rôle
        expires_delta=access_token_expires
    )
    return {"access_token": token, "token_type": "bearer"}



# CURRENT USER
@router.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user




@router.post("/forgot-password")
async def forgot_password(fpr: ForgotPasswordRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = get_user_by_email(db, fpr.email)
    if not user:
        # Pas d'information sur l'existence du user pour sécurité
        return {"msg": "If this email exists, a reset link has been sent."}

    token = create_reset_token(user.email)
    await send_reset_password_email(user.email, token, background_tasks)
    return {"msg": "If this email exists, a reset link has been sent."}


@router.post("/reset-password")
async def reset_password(rpr: ResetPasswordRequest, db: Session = Depends(get_db)):
    if rpr.new_password != rpr.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")

    email = decode_reset_token(rpr.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token.")

    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.hashed_password = hash_password(rpr.new_password)
    db.add(user)
    db.commit()
    return {"msg": "Password reset successfully."}

