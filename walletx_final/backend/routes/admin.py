from __future__ import annotations
import hmac
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from core.config import get_settings
from core.dependencies import get_admin_user
from core.security import create_access_token, verify_password, hash_password
from db.database import get_db
from middleware.rate_limiter import limiter
from models.entities import FraudAlert, Transaction, User, UserSession, Wallet
from schemas.schemas import AdminLogin, AdminStats, FraudAlertOut, Token, UserOut

router = APIRouter(prefix="/admin", tags=["Admin"])
settings = get_settings()


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def admin_login(request: Request, payload: AdminLogin, db: Session = Depends(get_db)):
    """Separate admin login — completely independent of user login."""
    if payload.email.lower() != settings.ADMIN_EMAIL.lower():
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    if not settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=503, detail="Admin password not configured")
    if not hmac.compare_digest(payload.password, settings.ADMIN_PASSWORD):
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

    admin = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not admin:
        admin = User(
            name="Admin",
            email=payload.email.lower(),
            hashed_password=hash_password(payload.password),
            is_admin=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

    session = UserSession(user_id=admin.id, is_active=True)
    db.add(session)
    db.commit()
    db.refresh(session)

    token = create_access_token(admin.id, session.id, is_admin=True)
    return Token(access_token=token, user=UserOut.model_validate(admin))


@router.get("/stats", response_model=AdminStats)
def get_stats(db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    total_users = db.scalar(select(func.count()).select_from(User).where(User.is_admin == False)) or 0
    total_txs = db.scalar(select(func.count()).select_from(Transaction)) or 0
    total_vol = db.scalar(select(func.sum(Transaction.amount)).select_from(Transaction)) or Decimal("0")
    fraud_count = db.scalar(select(func.count()).select_from(FraudAlert)) or 0
    active_sessions = db.scalar(select(func.count()).select_from(UserSession).where(UserSession.is_active == True)) or 0

    return AdminStats(
        total_users=total_users,
        total_transactions=total_txs,
        total_volume=total_vol,
        fraud_alerts=fraud_count,
        active_sessions=active_sessions,
    )


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    return db.scalars(select(User).where(User.is_admin == False).order_by(User.created_at.desc())).all()


@router.get("/fraud-alerts", response_model=list[FraudAlertOut])
def list_fraud_alerts(db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    return db.scalars(select(FraudAlert).order_by(FraudAlert.created_at.desc()).limit(100)).all()


@router.get("/transactions", response_model=list)
def list_all_transactions(db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    txs = db.scalars(
        select(Transaction)
        .options(selectinload(Transaction.fraud_alerts))
        .order_by(Transaction.timestamp.desc())
        .limit(200)
    ).all()
    return [
        {
            "id": t.id,
            "sender_id": t.sender_id,
            "receiver_id": t.receiver_id,
            "amount": str(t.amount),
            "status": t.status,
            "timestamp": t.timestamp.isoformat(),
            "flagged": len(t.fraud_alerts) > 0,
        }
        for t in txs
    ]


@router.put("/users/{user_id}/deactivate")
def deactivate_user(user_id: int, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_admin:
        raise HTTPException(status_code=403, detail="Cannot deactivate admin accounts")
    user.is_active = False
    db.commit()
    return {"message": f"User {user_id} deactivated"}
