from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from ..db import get_db
from ..auth import get_current_user
from .. import models, schemas

router = APIRouter(prefix="/api", tags=["crud"])

# ---- Categories ----
@router.get("/categories", response_model=List[schemas.CategoryRead])
def list_categories(db: Session = Depends(get_db), user=Depends(get_current_user)):
    items = db.query(models.Category).filter(models.Category.user_id==user.id, models.Category.deleted==False).all()
    return items

@router.post("/categories", response_model=schemas.CategoryRead)
def create_category(payload: schemas.CategoryCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    it = models.Category(**payload.model_dump(), user_id=user.id)
    db.add(it); db.commit(); db.refresh(it); return it

@router.put("/categories/{uuid}", response_model=schemas.CategoryRead)
def update_category(uuid: str, payload: schemas.CategoryCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    it = db.query(models.Category).filter(models.Category.uuid==uuid, models.Category.user_id==user.id).first()
    if not it: raise HTTPException(404, "Not found")
    for k,v in payload.model_dump().items(): setattr(it, k, v)
    db.commit(); db.refresh(it); return it

@router.delete("/categories/{uuid}")
def delete_category(uuid: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    it = db.query(models.Category).filter(models.Category.uuid==uuid, models.Category.user_id==user.id).first()
    if not it: raise HTTPException(404, "Not found")
    it.deleted = True; db.commit(); return {"ok": True}

# ---- Transactions ----
@router.get("/transactions", response_model=List[schemas.TransactionRead])
def list_transactions(
    start: Optional[str] = None,
    end: Optional[str] = None,
    type: Optional[str] = None,
    db: Session = Depends(get_db), user=Depends(get_current_user)):
    q = db.query(models.Transaction).filter(models.Transaction.user_id==user.id, models.Transaction.deleted==False)
    if type: q = q.filter(models.Transaction.type==type)
    if start:
        q = q.filter(models.Transaction.date >= datetime.fromisoformat(start))
    if end:
        q = q.filter(models.Transaction.date < datetime.fromisoformat(end))
    return q.order_by(models.Transaction.date.desc()).all()

@router.post("/transactions", response_model=schemas.TransactionRead)
def create_transaction(payload: schemas.TransactionCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    it = models.Transaction(**payload.model_dump(), user_id=user.id)
    db.add(it); db.commit(); db.refresh(it); return it

@router.put("/transactions/{uuid}", response_model=schemas.TransactionRead)
def update_transaction(uuid: str, payload: schemas.TransactionCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    it = db.query(models.Transaction).filter(models.Transaction.uuid==uuid, models.Transaction.user_id==user.id).first()
    if not it: raise HTTPException(404, "Not found")
    for k,v in payload.model_dump().items(): setattr(it, k, v)
    db.commit(); db.refresh(it); return it

@router.delete("/transactions/{uuid}")
def delete_transaction(uuid: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    it = db.query(models.Transaction).filter(models.Transaction.uuid==uuid, models.Transaction.user_id==user.id).first()
    if not it: raise HTTPException(404, "Not found")
    it.deleted = True; db.commit(); return {"ok": True}

# ---- Budgets ----
@router.get("/budgets", response_model=List[schemas.BudgetRead])
def list_budgets(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.Budget).filter(models.Budget.user_id==user.id, models.Budget.deleted==False).all()

@router.post("/budgets", response_model=schemas.BudgetRead)
def create_budget(payload: schemas.BudgetCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    it = models.Budget(**payload.model_dump(), user_id=user.id)
    db.add(it); db.commit(); db.refresh(it); return it

@router.put("/budgets/{uuid}", response_model=schemas.BudgetRead)
def update_budget(uuid: str, payload: schemas.BudgetCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    it = db.query(models.Budget).filter(models.Budget.uuid==uuid, models.Budget.user_id==user.id).first()
    if not it: raise HTTPException(404, "Not found")
    for k,v in payload.model_dump().items(): setattr(it, k, v)
    db.commit(); db.refresh(it); return it

@router.delete("/budgets/{uuid}")
def delete_budget(uuid: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    it = db.query(models.Budget).filter(models.Budget.uuid==uuid, models.Budget.user_id==user.id).first()
    if not it: raise HTTPException(404, "Not found")
    it.deleted = True; db.commit(); return {"ok": True}

# ---- Goals ----
@router.get("/goals", response_model=List[schemas.GoalRead])
def list_goals(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.Goal).filter(models.Goal.user_id==user.id, models.Goal.deleted==False).all()

@router.post("/goals", response_model=schemas.GoalRead)
def create_goal(payload: schemas.GoalCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    it = models.Goal(**payload.model_dump(), user_id=user.id)
    db.add(it); db.commit(); db.refresh(it); return it

@router.put("/goals/{uuid}", response_model=schemas.GoalRead)
def update_goal(uuid: str, payload: schemas.GoalCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    it = db.query(models.Goal).filter(models.Goal.uuid==uuid, models.Goal.user_id==user.id).first()
    if not it: raise HTTPException(404, "Not found")
    for k,v in payload.model_dump().items(): setattr(it, k, v)
    db.commit(); db.refresh(it); return it

@router.delete("/goals/{uuid}")
def delete_goal(uuid: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    it = db.query(models.Goal).filter(models.Goal.uuid==uuid, models.Goal.user_id==user.id).first()
    if not it: raise HTTPException(404, "Not found")
    it.deleted = True; db.commit(); return {"ok": True}
