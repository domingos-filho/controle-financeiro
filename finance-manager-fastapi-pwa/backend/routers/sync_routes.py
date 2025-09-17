from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from ..db import get_db
from ..auth import get_current_user
from .. import models, schemas

router = APIRouter(prefix="/api/sync", tags=["sync"])

def _merge(db, table, user_id, items, keys=('uuid',), date_field='updated_at'):
    upserted = 0
    for payload in items:
        data = payload.model_dump()
        # Find existing by uuid
        obj = db.query(table).filter(getattr(table, 'uuid')==data['uuid'], table.user_id==user_id).first()
        if obj:
            # basic conflict resolution by updated_at
            incoming = data.get(date_field) or datetime.utcnow()
            current = getattr(obj, date_field) or obj.created_at
            if incoming >= current:
                for k,v in data.items():
                    if hasattr(obj, k): setattr(obj, k, v)
                setattr(obj, 'user_id', user_id)
                upserted += 1
        else:
            obj = table(**data, user_id=user_id)
            db.add(obj); upserted += 1
    return upserted

@router.post("/push")
def push(payload: schemas.SyncPayload, db: Session = Depends(get_db), user=Depends(get_current_user)):
    upserted = 0
    upserted += _merge(db, models.Category, user.id, payload.categories)
    upserted += _merge(db, models.Transaction, user.id, payload.transactions)
    upserted += _merge(db, models.Budget, user.id, payload.budgets)
    upserted += _merge(db, models.Goal, user.id, payload.goals)
    db.add(models.SyncLog(user_id=user.id, direction="push", items=upserted, success=True))
    db.commit()
    return {"status": "ok", "upserted": upserted}

@router.get("/logs")
def logs(db: Session = Depends(get_db), user=Depends(get_current_user)):
    items = db.query(models.SyncLog).filter(models.SyncLog.user_id==user.id).order_by(models.SyncLog.created_at.desc()).limit(50).all()
    return [{"ts": i.created_at, "direction": i.direction, "items": i.items, "success": i.success, "message": i.message} for i in items]
