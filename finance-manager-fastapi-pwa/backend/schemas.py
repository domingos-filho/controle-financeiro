from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List

# ---- Auth ----
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int

# ---- Domain ----
class CategoryBase(BaseModel):
    uuid: str
    name: str
    type: str
    color: Optional[str] = None
    deleted: bool = False
    updated_at: Optional[datetime] = None

class CategoryCreate(CategoryBase): pass
class CategoryRead(CategoryBase):
    id: int

class TransactionBase(BaseModel):
    uuid: str
    type: str
    amount: float
    description: Optional[str] = None
    category_id: Optional[int] = None
    date: datetime
    deleted: bool = False
    updated_at: Optional[datetime] = None

class TransactionCreate(TransactionBase): pass
class TransactionRead(TransactionBase):
    id: int

class BudgetBase(BaseModel):
    uuid: str
    month: str
    category_id: Optional[int] = None
    limit_amount: float
    deleted: bool = False
    updated_at: Optional[datetime] = None

class BudgetCreate(BudgetBase): pass
class BudgetRead(BudgetBase):
    id: int

class GoalBase(BaseModel):
    uuid: str
    name: str
    target_amount: float
    current_amount: float = 0.0
    deadline: Optional[datetime] = None
    deleted: bool = False
    updated_at: Optional[datetime] = None

class GoalCreate(GoalBase): pass
class GoalRead(GoalBase):
    id: int

# ---- Sync payload ----
class SyncPayload(BaseModel):
    categories: List[CategoryCreate] = []
    transactions: List[TransactionCreate] = []
    budgets: List[BudgetCreate] = []
    goals: List[GoalCreate] = []

class ReportSummary(BaseModel):
    month: str
    income: float
    expenses: float
    net: float
