from __future__ import annotations
import hashlib
import hmac
import secrets
import resend

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.config import get_settings
from models.entities import OTPCode, User

settings = get_settings()
MAX_ATTEMPTS = 5


# FIX #1: secrets instead of random
def _generate_code() -> str:
    return "".join(secrets.choice("0123456789") for _ in range(6))


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def _send_email(to: str, code: str, name: str) -> None:
    if not settings.RESEND_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="RESEND_API_KEY is not configured",
        )

    resend.api_key = settings.RESEND_API_KEY

    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:500px;margin:auto;padding:30px">
        <h2 style="color:#4F46E5;">WalletX</h2>

        <p>Hello <strong>{name}</strong>,</p>

        <p>Your WalletX verification code is:</p>

        <div style="
            font-size:42px;
            font-weight:bold;
            letter-spacing:8px;
            margin:25px 0;
        ">
            {code}
        </div>

        <p>This code expires in {settings.OTP_EXPIRE_MINUTES} minutes.</p>

        <p>Please do not share this code with anyone.</p>
    </div>
    """

    try:
        resend.Emails.send(
            {
                "from": "WalletX <onboarding@resend.dev>",
                "to": [to],
                "subject": "Your WalletX OTP",
                "html": html,
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Email delivery failed: {e}",
        )
    


def issue_otp(db: Session, user: User) -> None:
    # Invalidate old unused codes
    old = db.scalars(select(OTPCode).where(
        OTPCode.user_id == user.id,
        OTPCode.is_used == False,
        OTPCode.purpose == "login",
    )).all()
    for o in old:
        o.is_used = True

    code = _generate_code()
    otp = OTPCode(
        user_id=user.id,
        code_hash=_hash_code(code),
        purpose="login",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES),
    )
    db.add(otp)
    db.commit()
    _send_email(user.email, code, user.name)


def verify_otp(db: Session, user: User, code: str) -> None:
    otp = db.scalar(
        select(OTPCode)
        .where(OTPCode.user_id == user.id, OTPCode.is_used == False, OTPCode.purpose == "login")
        .order_by(OTPCode.created_at.desc())
    )

    if otp is None:
        raise HTTPException(status_code=400, detail="No active OTP. Request a new one.")

    if datetime.now(timezone.utc) > otp.expires_at:
        otp.is_used = True
        db.commit()
        raise HTTPException(status_code=400, detail="OTP expired. Request a new one.")

    if otp.attempts >= MAX_ATTEMPTS:
        otp.is_used = True
        db.commit()
        raise HTTPException(status_code=400, detail="Too many attempts. Request a new OTP.")

    # FIX #3: timing-safe comparison
    if not hmac.compare_digest(otp.code_hash, _hash_code(code)):
        otp.attempts += 1
        db.commit()
        remaining = MAX_ATTEMPTS - otp.attempts
        raise HTTPException(status_code=400, detail=f"Wrong code. {remaining} attempts left.")

    otp.is_used = True
    db.commit()
