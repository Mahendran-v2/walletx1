from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.entities import User, Wallet
from core.security import hash_password, verify_password
from schemas.schemas import UserCreate, UserUpdate
from decimal import Decimal


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def authenticate(db: Session, email: str, password: str) -> User:
    user = get_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")
    return user


def create_user(db: Session, payload: UserCreate) -> User:
    if get_by_email(db, payload.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        name=payload.name,
        email=payload.email.lower(),
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.flush()
    wallet = Wallet(user_id=user.id, balance=Decimal("0.00"))
    db.add(wallet)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User, payload: UserUpdate) -> User:
    if payload.name:
        user.name = payload.name
    if payload.email:
        existing = get_by_email(db, payload.email)
        if existing and existing.id != user.id:
            raise HTTPException(status_code=409, detail="Email already in use")
        user.email = payload.email.lower()
    if payload.password:
        user.hashed_password = hash_password(payload.password)
    db.commit()
    db.refresh(user)
    return user
