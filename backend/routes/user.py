from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.dependencies import get_current_user
from db.database import get_db
from models.entities import User
from schemas.schemas import UserOut, UserUpdate
from services import user_service

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("", response_model=UserOut)
def get_profile(user: User = Depends(get_current_user)):
    return user


@router.put("", response_model=UserOut)
def update_profile(payload: UserUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return user_service.update_user(db, user, payload)
