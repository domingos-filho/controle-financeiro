from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import List
from ..db import get_db
from ..auth import get_current_user
from .. import models, schemas

router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.get("/summary")
def summary(db: Session = Depends(get_db), user=Depends(get_current_user)):
    # Aggregate by month (YYYY-MM)
    txs = db.query(models.Transaction).filter(models.Transaction.user_id==user.id, models.Transaction.deleted==False).all()
    data = {}
    for t in txs:
        m = t.date.strftime("%Y-%m")
        if m not in data: data[m] = {"income":0.0, "expenses":0.0}
        if t.type == "income": data[m]["income"] += t.amount
        else: data[m]["expenses"] += t.amount
    out = []
    for m,v in sorted(data.items()):
        out.append({"month": m, "income": v["income"], "expenses": v["expenses"], "net": v["income"]-v["expenses"]})
    return out

@router.get("/by-category")
def by_category(db: Session = Depends(get_db), user=Depends(get_current_user)):
    # Sum amount by category for current month
    now = datetime.utcnow()
    start = datetime(now.year, now.month, 1)
    end = datetime(now.year+1,1,1) if now.month==12 else datetime(now.year, now.month+1, 1)
    rows = db.query(models.Category.name, func.sum(models.Transaction.amount)).join(models.Transaction, models.Transaction.category_id==models.Category.id, isouter=True).filter(
        models.Category.user_id==user.id, models.Category.deleted==False, models.Transaction.deleted==False, models.Transaction.date>=start, models.Transaction.date<end, models.Transaction.type=="expense"
    ).group_by(models.Category.name).all()
    return [{"category": r[0], "value": float(r[1] or 0)} for r in rows]
