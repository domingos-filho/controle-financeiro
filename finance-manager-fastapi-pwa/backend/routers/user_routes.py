from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from ..auth import get_current_user
from .. import models, schemas

router = APIRouter(prefix="/api", tags=["users"])

@router.get("/me", response_model=schemas.UserRead)
def me(user: models.User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "full_name": user.full_name}
