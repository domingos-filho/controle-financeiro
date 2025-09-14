from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional
from .. import models, schemas
from ..database import SessionLocal
from .auth import get_current_user

router = APIRouter(prefix="/finance", tags=["finance"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Categories
@router.post("/categories", response_model=schemas.Category)
def create_category(cat: schemas.CategoryCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    db_cat = models.Category(name=cat.name, type=cat.type, user_id=user.id)
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat

@router.get("/categories", response_model=List[schemas.Category])
def list_categories(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return db.query(models.Category).filter(models.Category.user_id == user.id).all()

# Transactions
@router.post("/transactions", response_model=schemas.Transaction)
def create_transaction(tx: schemas.TransactionCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    db_tx = models.Transaction(**tx.dict(), user_id=user.id)
    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)
    return db_tx

@router.get("/transactions", response_model=List[schemas.Transaction])
def list_transactions(
    start: Optional[date] = None,
    end: Optional[date] = None,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    q = db.query(models.Transaction).filter(models.Transaction.user_id == user.id)
    if start:
        q = q.filter(models.Transaction.date >= start)
    if end:
        q = q.filter(models.Transaction.date <= end)
    return q.order_by(models.Transaction.date.desc()).all()

# Goals
@router.post("/goals", response_model=schemas.Goal)
def create_goal(goal: schemas.GoalCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    db_goal = models.Goal(**goal.dict(), user_id=user.id)
    db.add(db_goal); db.commit(); db.refresh(db_goal); return db_goal

@router.get("/goals", response_model=List[schemas.Goal])
def list_goals(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return db.query(models.Goal).filter(models.Goal.user_id == user.id).all()

# Offline sync: receives a list of transactions and upserts by (date, amount, description)
@router.post("/sync")
def sync_transactions(items: List[schemas.TransactionCreate], db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    inserted = 0
    for it in items:
        exists = (
            db.query(models.Transaction)
            .filter(
                models.Transaction.user_id == user.id,
                models.Transaction.date == it.date,
                models.Transaction.amount == it.amount,
                models.Transaction.description == it.description,
            ).first()
        )
        if not exists:
            db.add(models.Transaction(**it.dict(), user_id=user.id))
            inserted += 1
    db.commit()
    return {"inserted": inserted, "received": len(items)}
