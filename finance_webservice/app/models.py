from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, default="")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    categories = relationship("Category", back_populates="owner")
    transactions = relationship("Transaction", back_populates="owner")
    budgets = relationship("Budget", back_populates="owner")
    goals = relationship("Goal", back_populates="owner")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    type = Column(String, nullable=False)  # 'income' or 'expense'
    color = Column(String, default="#8884d8")
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")

    __table_args__ = (UniqueConstraint('name', 'type', 'user_id', name='uq_cat_user'),)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    description = Column(String, default="")
    amount = Column(Float, nullable=False)  # positive for income, negative for expense
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    origin = Column(String, default="server")  # 'server' or 'client'
    client_uuid = Column(String, nullable=True) # to deduplicate offline sync
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")

class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True, index=True)
    month = Column(String, index=True)  # 'YYYY-MM'
    amount = Column(Float, default=0.0) # total expense budget
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="budgets")
    __table_args__ = (UniqueConstraint('month', 'user_id', name='uq_budget_user_month'),)

class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    target_amount = Column(Float, default=0.0)
    current_amount = Column(Float, default=0.0)
    deadline = Column(Date, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="goals")

class SyncLog(Base):
    __tablename__ = "sync_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)  # 'push' or 'pull'
    count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
