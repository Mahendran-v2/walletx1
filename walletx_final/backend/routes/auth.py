from __future__ import annotations
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.dependencies import get_current_user
from core.security import create_access_token
from db.database import get_db
from middleware.rate_limiter import limiter
from models.entities import User, UserSession
from schemas.schemas import OTPRequest, OTPVerify, Token, UserCreate, UserOut
from services import otp_service, user_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db, payload)


@router.post("/login/request-otp")
@limiter.limit("5/minute")
def request_otp(request: Request, payload: OTPRequest, db: Session = Depends(get_db)):
    user = user_service.authenticate(db, payload.email, payload.password)
    otp_service.issue_otp(db, user)
    return {"message": "OTP sent to your email"}


@router.post("/login/verify-otp", response_model=Token)
@limiter.limit("10/minute")
def verify_otp(request: Request, payload: OTPVerify, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user:
        raise HTTPException(status_code=400, detail="Invalid request")

    otp_service.verify_otp(db, user, payload.code)

    session = UserSession(user_id=user.id, is_active=True)
    db.add(session)
    db.commit()
    db.refresh(session)

    token = create_access_token(user.id, session.id, user.is_admin)
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sessions = db.scalars(
        select(UserSession).where(
            UserSession.user_id == current_user.id,
            UserSession.is_active == True,
        )
    ).all()
    for s in sessions:
        s.is_active = False
    db.commit()
    return {"message": "Logged out"}
