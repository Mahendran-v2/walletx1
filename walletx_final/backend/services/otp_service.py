from __future__ import annotations
import hashlib
import hmac
import secrets
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        if settings.ENV == "production":
            raise HTTPException(status_code=503, detail="Email service not configured")
        print(f"\n[DEV OTP] Email not configured — code for {to}: {code}\n", flush=True)
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Your WalletX code: {code}"
    msg["From"] = settings.SMTP_FROM or settings.SMTP_USER
    msg["To"] = to

    html = f"""
    <div style="font-family:Inter,sans-serif;max-width:480px;margin:0 auto;background:#0A0F1E;color:#F8FAFC;padding:40px;border-radius:16px">
      <h2 style="color:#6366F1">WalletX</h2>
      <p>Hi {name}, your login code is:</p>
      <div style="font-size:48px;font-weight:700;letter-spacing:12px;color:#fff;margin:24px 0">{code}</div>
      <p style="color:#94A3B8">Expires in {settings.OTP_EXPIRE_MINUTES} minutes. Do not share this code.</p>
    </div>"""

    msg.attach(MIMEText(f"Your WalletX OTP: {code}", "plain"))
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as s:
            s.starttls()
            s.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            s.sendmail(msg["From"], [to], msg.as_string())
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Email delivery failed: {e}")


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
