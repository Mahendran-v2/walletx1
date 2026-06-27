from __future__ import annotations
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from core.security import decode_token
from db.database import get_db
from models.entities import User, UserSession

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/verify-otp")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token", headers={"WWW-Authenticate": "Bearer"})

    user_id = int(payload["sub"])
    session_id = payload.get("sid")

    session = db.get(UserSession, session_id)
    if not session or not session.is_active:
        raise HTTPException(status_code=401, detail="Session expired. Please log in again.")

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    return user


def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
