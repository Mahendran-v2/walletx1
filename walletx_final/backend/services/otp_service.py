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


def _generate_code() -> str:
    ...


def _hash_code(code: str) -> str:
    ...


# 👇 REPLACE ONLY THIS FUNCTION
def _send_email(...):
    ...


def issue_otp(...):
    ...


def verify_otp(...):
    ...
