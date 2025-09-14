from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
from .. import models, schemas
from ..database import SessionLocal
from .auth import get_current_user

router = APIRouter(prefix="/reports", tags=["reports"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/cashflow", response_model=schemas.CashflowSummary)
def cashflow(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    ins = db.query(models.Transaction).filter(models.Transaction.user_id == user.id, models.Transaction.type == "IN").all()
    outs = db.query(models.Transaction).filter(models.Transaction.user_id == user.id, models.Transaction.type == "OUT").all()
    total_in = sum(t.amount for t in ins)
    total_out = sum(t.amount for t in outs)
    return {"total_in": total_in, "total_out": total_out, "balance": total_in - total_out}
