from __future__ import annotations
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import func as sqlfunc, or_, select
from sqlalchemy.orm import Session, selectinload

from models.entities import FraudAlert, Transaction, User, Wallet
from core.config import get_settings

settings = get_settings()


def get_wallet(db: Session, user_id: int, lock: bool = False) -> Wallet:
    q = select(Wallet).where(Wallet.user_id == user_id)
    if lock:
        q = q.with_for_update()
    wallet = db.scalar(q)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet


# FIX #2: with_for_update on add and withdraw too
def add_money(db: Session, user: User, amount: Decimal) -> Wallet:
    wallet = get_wallet(db, user.id, lock=True)
    wallet.balance = Decimal(str(wallet.balance)) + amount
    wallet.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(wallet)
    return wallet


def withdraw_money(db: Session, user: User, amount: Decimal) -> Wallet:
    wallet = get_wallet(db, user.id, lock=True)
    if Decimal(str(wallet.balance)) < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    wallet.balance = Decimal(str(wallet.balance)) - amount
    wallet.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(wallet)
    return wallet


def transfer_money(db: Session, sender: User, receiver_id: int, amount: Decimal, note: str | None) -> Transaction:
    if sender.id == receiver_id:
        raise HTTPException(status_code=400, detail="Cannot transfer to yourself")

    receiver = db.get(User, receiver_id)
    if not receiver:
        raise HTTPException(status_code=404, detail="Recipient not found")

    # Lock both wallets atomically
    sender_wallet = db.scalar(select(Wallet).where(Wallet.user_id == sender.id).with_for_update())
    receiver_wallet = db.scalar(select(Wallet).where(Wallet.user_id == receiver.id).with_for_update())

    if not sender_wallet or not receiver_wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    if Decimal(str(sender_wallet.balance)) < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    try:
        sender_wallet.balance = Decimal(str(sender_wallet.balance)) - amount
        receiver_wallet.balance = Decimal(str(receiver_wallet.balance)) + amount

        tx = Transaction(
            sender_id=sender.id,
            receiver_id=receiver.id,
            amount=amount,
            status="success",
            note=note,
        )
        db.add(tx)
        db.flush()

        _run_fraud_checks(db, tx, sender)
        db.commit()
        db.refresh(tx)
        return tx

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Transfer failed. No money was moved.") from e


def _run_fraud_checks(db: Session, tx: Transaction, sender: User) -> None:
    alerts = []
    threshold = Decimal(str(settings.FRAUD_AMOUNT_THRESHOLD))
    rate_limit = settings.FRAUD_RATE_LIMIT
    avg_mult = Decimal(str(settings.FRAUD_AVG_MULTIPLIER))

    if tx.amount > threshold:
        alerts.append(FraudAlert(transaction_id=tx.id, rule_triggered="LARGE_TRANSFER", severity="high"))

    one_min_ago = datetime.now(timezone.utc) - timedelta(minutes=1)
    recent_count = db.scalar(
        select(sqlfunc.count()).select_from(Transaction)
        .where(Transaction.sender_id == sender.id, Transaction.timestamp >= one_min_ago, Transaction.id != tx.id)
    ) or 0
    if recent_count >= rate_limit:
        alerts.append(FraudAlert(transaction_id=tx.id, rule_triggered="VELOCITY_BREACH", severity="medium"))

    avg = db.scalar(
        select(sqlfunc.avg(Transaction.amount))
        .where(Transaction.sender_id == sender.id, Transaction.id != tx.id)
    )
    if avg and tx.amount > Decimal(str(avg)) * avg_mult:
        alerts.append(FraudAlert(transaction_id=tx.id, rule_triggered="UNUSUAL_AMOUNT", severity="medium"))

    for a in alerts:
        db.add(a)


def get_transactions(db: Session, user: User) -> list[Transaction]:
    return list(db.scalars(
        select(Transaction)
        .where(or_(Transaction.sender_id == user.id, Transaction.receiver_id == user.id))
        .options(selectinload(Transaction.fraud_alerts))
        .order_by(Transaction.timestamp.desc())
        .limit(200)
    ).all())
