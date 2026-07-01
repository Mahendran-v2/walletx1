from __future__ import annotations

import hashlib
import hmac
import secrets
import resend

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.config import get_settings
from models.entities import OTPCode, User
from core.config import get_settings
from models.entities import OTPCode, User

settings = get_settings()
MAX_ATTEMPTS = 5

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
        response = resend.Emails.send(
            {
                "from": "WalletX <onboarding@resend.dev>",
                "to": [to],
                "subject": "Your WalletX OTP",
                "html": html,
            }
        )

        print("Resend Response:", response)

    except Exception as e:
        import traceback
        traceback.print_exc()

        print("RESEND ERROR:", repr(e))

        raise HTTPException(
            status_code=503,
            detail=f"Email delivery failed: {e}",
        )