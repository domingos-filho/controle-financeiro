from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from .database import Base, engine, get_db
from . import models, schemas, security

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Finance Web Service", version="1.0.0")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# serve frontend
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

# --------------- Auth ---------------
@app.post("/api/auth/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    u = models.User(email=user.email, full_name=user.full_name, hashed_password=security.hash_password(user.password))
    db.add(u); db.commit(); db.refresh(u)
    # create default categories
    defaults = [
        ("Salário", "income", "#22c55e"),
        ("Outras Receitas", "income", "#10b981"),
        ("Alimentação", "expense", "#ef4444"),
        ("Transporte", "expense", "#f59e0b"),
        ("Moradia", "expense", "#7c3aed"),
        ("Lazer", "expense", "#3b82f6"),
    ]
    for name, t, color in defaults:
        db.add(models.Category(name=name, type=t, color=color, owner=u))
    db.commit()
    return u

@app.post("/api/auth/token", response_model=schemas.Token)
def login(form_data: security.OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = security.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    token = security.create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

# --------------- Categories ---------------
@app.get("/api/categories", response_model=List[schemas.CategoryOut])
def list_categories(current=Depends(security.get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Category).filter(models.Category.user_id == current.id).order_by(models.Category.type, models.Category.name).all()

@app.post("/api/categories", response_model=schemas.CategoryOut)
def create_category(cat: schemas.CategoryIn, current=Depends(security.get_current_user), db: Session = Depends(get_db)):
    c = models.Category(**cat.dict(), user_id=current.id)
    db.add(c); db.commit(); db.refresh(c); return c

# --------------- Transactions ---------------
@app.get("/api/transactions", response_model=List[schemas.TransactionOut])
def list_transactions(month: str | None = None, current=Depends(security.get_current_user), db: Session = Depends(get_db)):
    q = db.query(models.Transaction).filter(models.Transaction.user_id == current.id)
    if month:  # format YYYY-MM
        y, m = month.split("-")
        q = q.filter(models.Transaction.date >= date(int(y), int(m), 1))
        if int(m) == 12:
            q = q.filter(models.Transaction.date < date(int(y)+1, 1, 1))
        else:
            q = q.filter(models.Transaction.date < date(int(y), int(m)+1, 1))
    return q.order_by(models.Transaction.date.desc(), models.Transaction.id.desc()).all()

@app.post("/api/transactions", response_model=schemas.TransactionOut)
def create_txn(txn: schemas.TransactionIn, current=Depends(security.get_current_user), db: Session = Depends(get_db)):
    t = models.Transaction(**txn.dict(), user_id=current.id)
    db.add(t); db.commit(); db.refresh(t); return t

@app.delete("/api/transactions/{txn_id}")
def delete_txn(txn_id: int, current=Depends(security.get_current_user), db: Session = Depends(get_db)):
    t = db.query(models.Transaction).filter(models.Transaction.id==txn_id, models.Transaction.user_id==current.id).first()
    if not t: raise HTTPException(status_code=404, detail="Not found")
    db.delete(t); db.commit(); return {"ok": True}

# bulk sync for offline
@app.post("/api/sync/push")
def sync_push(payload: schemas.SyncPayload, current=Depends(security.get_current_user), db: Session = Depends(get_db)):
    inserted = 0
    for tr in payload.transactions:
        # dedupe by client_uuid if present
        if tr.client_uuid:
            exists = db.query(models.Transaction).filter(models.Transaction.user_id==current.id, models.Transaction.client_uuid==tr.client_uuid).first()
            if exists: continue
        t = models.Transaction(**tr.dict(), user_id=current.id, origin="client")
        db.add(t); inserted += 1
    db.add(models.SyncLog(user_id=current.id, action="push", count=inserted))
    db.commit()
    return {"inserted": inserted}

# --------------- Budgets & Goals ---------------
@app.get("/api/budgets", response_model=List[schemas.BudgetOut])
def list_budgets(current=Depends(security.get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Budget).filter(models.Budget.user_id==current.id).all()

@app.post("/api/budgets", response_model=schemas.BudgetOut)
def set_budget(b: schemas.BudgetIn, current=Depends(security.get_current_user), db: Session = Depends(get_db)):
    existing = db.query(models.Budget).filter(models.Budget.user_id==current.id, models.Budget.month==b.month).first()
    if existing:
        existing.amount = b.amount; db.commit(); db.refresh(existing); return existing
    obj = models.Budget(**b.dict(), user_id=current.id); db.add(obj); db.commit(); db.refresh(obj); return obj

@app.get("/api/goals", response_model=List[schemas.GoalOut])
def list_goals(current=Depends(security.get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Goal).filter(models.Goal.user_id==current.id).all()

@app.post("/api/goals", response_model=schemas.GoalOut)
def create_goal(g: schemas.GoalIn, current=Depends(security.get_current_user), db: Session = Depends(get_db)):
    obj = models.Goal(**g.dict(), user_id=current.id); db.add(obj); db.commit(); db.refresh(obj); return obj

# --------------- Reports ---------------
@app.get("/api/reports/summary")
def summary(month: str | None = None, current=Depends(security.get_current_user), db: Session = Depends(get_db)):
    from sqlalchemy import func, case
    q = db.query(models.Transaction).filter(models.Transaction.user_id==current.id)
    if month:
        y, m = map(int, month.split("-"))
        from datetime import date
        q = q.filter(models.Transaction.date >= date(y, m, 1))
        q = q.filter(models.Transaction.date < date(y+1,1,1) if m==12 else models.Transaction.date < date(y, m+1, 1))
    totals = db.query(func.sum(models.Transaction.amount)).filter(models.Transaction.user_id==current.id).scalar() or 0.0
    income = db.query(func.sum(models.Transaction.amount)).filter(models.Transaction.user_id==current.id, models.Transaction.amount>0).scalar() or 0.0
    expense = db.query(func.sum(models.Transaction.amount)).filter(models.Transaction.user_id==current.id, models.Transaction.amount<0).scalar() or 0.0
    # by category
    cat_rows = db.query(models.Category.name, func.sum(models.Transaction.amount)).join(models.Transaction, models.Transaction.category_id==models.Category.id, isouter=True).filter(models.Category.user_id==current.id).group_by(models.Category.name).all()
    by_cat = [{"category": name, "amount": float(total or 0)} for name, total in cat_rows]
    return {"total": float(totals), "income": float(income), "expense": float(expense), "by_category": by_cat}
