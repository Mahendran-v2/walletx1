from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.dependencies import get_current_user
from db.database import get_db
from models.entities import User
from schemas.schemas import AmountIn, TransactionOut, TransferIn, WalletOut
from services import wallet_service

router = APIRouter(prefix="/wallet", tags=["Wallet"])


@router.get("", response_model=WalletOut)
def get_wallet(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return wallet_service.get_wallet(db, user.id)


@router.post("/add", response_model=WalletOut)
def add_money(payload: AmountIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return wallet_service.add_money(db, user, payload.amount)


@router.post("/withdraw", response_model=WalletOut)
def withdraw(payload: AmountIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return wallet_service.withdraw_money(db, user, payload.amount)


@router.post("/transfer", response_model=TransactionOut)
def transfer(payload: TransferIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tx = wallet_service.transfer_money(db, user, payload.receiver_id, payload.amount, payload.note)
    return TransactionOut.from_orm_with_flag(tx)


@router.get("/transactions", response_model=list[TransactionOut])
def transactions(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    txs = wallet_service.get_transactions(db, user)
    return [TransactionOut.from_orm_with_flag(t) for t in txs]
