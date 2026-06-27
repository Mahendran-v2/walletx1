from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from core.config import get_settings
from db.database import init_db
from middleware.rate_limiter import limiter
from routes import auth, wallet, user, admin

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.validate_for_production()
    init_db()
    yield


app = FastAPI(
    title="WalletX API",
    description="Secure digital wallet backend",
    version="2.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(wallet.router)
app.include_router(user.router)
app.include_router(admin.router)


@app.get("/health", tags=["System"])
def health():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "cors": settings.CORS_ORIGINS
    }
