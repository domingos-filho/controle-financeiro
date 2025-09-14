from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import Optional, List

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(min_length=6)

class User(UserBase):
    id: int
    is_active: bool
    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    name: str
    type: str = "OUT"  # IN or OUT

class CategoryCreate(CategoryBase): pass

class Category(CategoryBase):
    id: int
    class Config:
        from_attributes = True

class TransactionBase(BaseModel):
    date: date
    description: str = ""
    type: str  # IN or OUT
    amount: float
    category_id: Optional[int] = None

class TransactionCreate(TransactionBase): pass

class Transaction(TransactionBase):
    id: int
    class Config:
        from_attributes = True

class GoalBase(BaseModel):
    name: str
    target_amount: float
    current_amount: float = 0
    deadline: Optional[date] = None

class GoalCreate(GoalBase): pass

class Goal(GoalBase):
    id: int
    class Config:
        from_attributes = True

class CashflowSummary(BaseModel):
    total_in: float
    total_out: float
    balance: float
