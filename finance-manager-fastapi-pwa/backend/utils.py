from sqlalchemy.orm import Session
from . import models
from datetime import datetime
from collections import defaultdict

def ensure_superuser(db: Session, email: str, password_hash: str):
    admin = db.query(models.User).filter(models.User.email == email).first()
    if not admin:
        admin = models.User(email=email, hashed_password=password_hash, is_superuser=True)
        db.add(admin)
        db.commit()

def suggestions(db: Session, user_id: int):
    # Very simple heuristics for demo: identify overspent categories vs budgets for current month
    now = datetime.utcnow()
    month = now.strftime("%Y-%m")
    budgets = db.query(models.Budget).filter(models.Budget.user_id==user_id, models.Budget.month==month, models.Budget.deleted==False).all()
    # Sum expenses per category this month
    start = datetime(now.year, now.month, 1)
    if now.month == 12:
        end = datetime(now.year+1, 1, 1)
    else:
        end = datetime(now.year, now.month+1, 1)
    txs = db.query(models.Transaction).filter(
        models.Transaction.user_id==user_id,
        models.Transaction.type=="expense",
        models.Transaction.date>=start, models.Transaction.date<end,
        models.Transaction.deleted==False
    ).all()
    spent = defaultdict(float)
    for t in txs: spent[t.category_id] += t.amount
    advice = []
    for b in budgets:
        s = spent.get(b.category_id, 0.0)
        if s > b.limit_amount:
            advice.append(f"Categoria {b.category_id}: gasto {s:.2f} excedeu o orçamento {b.limit_amount:.2f}. Considere reduzir despesas ou aumentar o limite.")
        elif s > 0.9*b.limit_amount:
            advice.append(f"Categoria {b.category_id}: você está em {s:.2f}, chegando perto do limite {b.limit_amount:.2f}.")
    # 50/30/20 rule suggestion
    income = sum(t.amount for t in db.query(models.Transaction).filter(
        models.Transaction.user_id==user_id, models.Transaction.type=="income", models.Transaction.date>=start, models.Transaction.date<end, models.Transaction.deleted==False))
    expenses = sum(t.amount for t in db.query(models.Transaction).filter(
        models.Transaction.user_id==user_id, models.Transaction.type=="expense", models.Transaction.date>=start, models.Transaction.date<end, models.Transaction.deleted==False))
    if income > 0:
        needs = expenses*0.6  # rough
        wants = expenses*0.3
        savings = income - expenses
        advice.append(f"Regra 50/30/20 (aprox.): garanta 50% necessidades, 30% desejos, 20% poupança. Poupança atual ~ {savings/income*100:.1f}%")
    return advice
