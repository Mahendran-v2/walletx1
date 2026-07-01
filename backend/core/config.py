from __future__ import annotations
import os
import secrets
import sys
from functools import lru_cache

# Load .env before reading any os.getenv so local dev works without
# manually exporting variables. In production (Railway) this is a no-op
# because python-dotenv skips loading if the vars are already set.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed; rely on shell env


class Settings:
    APP_NAME: str
    ENV: str
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    OTP_EXPIRE_MINUTES: int
    RESEND_API_KEY: str
    FRAUD_AMOUNT_THRESHOLD: int
    FRAUD_RATE_LIMIT: int
    FRAUD_AVG_MULTIPLIER: int
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str

    def __init__(self) -> None:
        self.APP_NAME = os.getenv("APP_NAME", "WalletX")
        self.ENV = os.getenv("ENV", "development")
        self.DATABASE_URL = os.getenv("DATABASE_URL", "")
        self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
        self.OTP_EXPIRE_MINUTES = int(os.getenv("OTP_EXPIRE_MINUTES", "10"))
        self.RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
        self.FRAUD_AMOUNT_THRESHOLD = int(os.getenv("FRAUD_AMOUNT_THRESHOLD", "10000"))
        self.FRAUD_RATE_LIMIT = int(os.getenv("FRAUD_RATE_LIMIT", "3"))
        self.FRAUD_AVG_MULTIPLIER = int(os.getenv("FRAUD_AVG_MULTIPLIER", "3"))
        self.ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@walletx.com")
        self.ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

        # Secret key — generate ephemeral if not set (warns loudly)
        raw_secret = os.getenv("SECRET_KEY", "")
        if raw_secret:
            self.SECRET_KEY = raw_secret
        else:
            self.SECRET_KEY = secrets.token_hex(32)
            print(
                "[WARNING] SECRET_KEY not set — generated ephemeral key. "
                "JWTs will be invalidated on every restart. Set SECRET_KEY in environment.",
                file=sys.stderr,
            )

    @property
    def CORS_ORIGINS(self) -> list[str]:
        raw = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
        return [o.strip() for o in raw.split(",") if o.strip()]

    def validate_for_production(self) -> None:
        fatal: list[str] = []
        warnings: list[str] = []

        if not self.DATABASE_URL:
            fatal.append("DATABASE_URL is not set")
        if not self.ADMIN_PASSWORD:
            fatal.append("ADMIN_PASSWORD is not set")
        if len(self.SECRET_KEY) < 32:
            fatal.append("SECRET_KEY must be at least 32 characters")
        if not os.getenv("SECRET_KEY"):
            warnings.append("SECRET_KEY not set — JWTs invalidated on every restart")
      

        for w in warnings:
            print(f"[WARNING] {w}", file=sys.stderr)

        if fatal:
            msg = "Startup aborted — missing required configuration:\n" + "\n".join(
                f"  ✗ {e}" for e in fatal
            )
            raise RuntimeError(msg)


@lru_cache
def get_settings() -> Settings:
    return Settings()
