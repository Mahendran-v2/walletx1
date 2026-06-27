from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict


# ── Auth ──────────────────────────────────────────────────────────────────────
class OTPRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)

class OTPVerify(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"

class AdminLogin(BaseModel):
    email: EmailStr
    password: str


# ── User ──────────────────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def strong_password(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    is_admin: bool
    created_at: datetime

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def strong_password(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


# ── Wallet ────────────────────────────────────────────────────────────────────
class WalletOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    balance: Decimal
    updated_at: datetime

class AmountIn(BaseModel):
    amount: Decimal = Field(gt=Decimal("0"), max_digits=12, decimal_places=2)


# ── Transfers ─────────────────────────────────────────────────────────────────
class TransferIn(BaseModel):
    receiver_id: int
    amount: Decimal = Field(gt=Decimal("0"), max_digits=12, decimal_places=2)
    note: Optional[str] = Field(None, max_length=255)

class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sender_id: int
    receiver_id: int
    amount: Decimal
    status: str
    note: Optional[str]
    timestamp: datetime
    is_flagged: bool = False

    @classmethod
    def from_orm_with_flag(cls, tx) -> "TransactionOut":
        obj = cls.model_validate(tx)
        obj.is_flagged = len(tx.fraud_alerts) > 0
        return obj


# ── Admin ─────────────────────────────────────────────────────────────────────
class AdminStats(BaseModel):
    total_users: int
    total_transactions: int
    total_volume: Decimal
    fraud_alerts: int
    active_sessions: int

class FraudAlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    transaction_id: int
    rule_triggered: str
    severity: str
    created_at: datetime
