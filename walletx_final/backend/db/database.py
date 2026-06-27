from __future__ import annotations
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from core.config import get_settings

settings = get_settings()


class Base(DeclarativeBase):
    pass


# Lazy globals — populated by init_db() at startup so a missing DATABASE_URL
# gives a clear error message instead of crashing at import time.
engine = None
SessionLocal = None


def _get_engine():
    global engine, SessionLocal
    if engine is None:
        if not settings.DATABASE_URL:
            raise RuntimeError(
                "DATABASE_URL is not set. Add it to your environment variables."
            )
        engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            echo=settings.ENV == "development",
        )
        SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    return engine


def get_db():
    if SessionLocal is None:
        _get_engine()
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    _get_engine()  # validates DATABASE_URL and creates engine
    from models import entities  # noqa: F401 — registers all models
    Base.metadata.create_all(bind=engine)
    print("[DB] Tables created / verified")
