from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = ""

class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class CategoryIn(BaseModel):
    name: str
    type: str
    color: Optional[str] = "#8884d8"

class CategoryOut(CategoryIn):
    id: int
    class Config:
        orm_mode = True

class TransactionIn(BaseModel):
    date: date
    description: Optional[str] = ""
    amount: float
    category_id: Optional[int] = None
    client_uuid: Optional[str] = None

class TransactionOut(TransactionIn):
    id: int
    class Config:
        orm_mode = True

class BudgetIn(BaseModel):
    month: str = Field(..., regex=r"\d{4}-\d{2}")
    amount: float

class BudgetOut(BudgetIn):
    id: int
    class Config:
        orm_mode = True

class GoalIn(BaseModel):
    name: str
    target_amount: float
    current_amount: float = 0.0
    deadline: Optional[date] = None

class GoalOut(GoalIn):
    id: int
    class Config:
        orm_mode = True

class SyncPayload(BaseModel):
    transactions: List[TransactionIn] = []
