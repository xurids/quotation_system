from sqlalchemy import Column, Integer, String, Numeric, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class QuotationTemplate(Base):
    __tablename__ = "quotation_templates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    code = Column(String(50), unique=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    status = Column(String(50), default="draft") # draft, auditing, approved, closed
    tax_rate = Column(Numeric(5, 4), default=0.0600)
    discount = Column(Numeric(5, 4), default=1.0000)
    total_budget = Column(Numeric(15, 2), default=0)
    development_total = Column(Numeric(15, 2), default=0)
    other_costs_total = Column(Numeric(15, 2), default=0)
    created_at = Column(DateTime, default=datetime.now)
    categories = relationship("ExpenseCategory", back_populates="project", cascade="all, delete-orphan")
    client = relationship("Client")

class ExpenseCategory(Base):
    __tablename__ = "expense_categories"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String(100))
    budget_amount = Column(Numeric(15, 2), default=0)
    project = relationship("Project", back_populates="categories")
    modules = relationship("FunctionModule", back_populates="category", cascade="all, delete-orphan")

class FunctionModule(Base):
    __tablename__ = "function_modules"
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("expense_categories.id"))
    system_name = Column(String(200))
    subsystem_name = Column(String(200))
    level1 = Column(String(200))
    level2 = Column(String(200))
    level3 = Column(String(200))
    level4 = Column(String(200))
    level5 = Column(String(200))
    description = Column(Text)
    work_months = Column(Numeric(10, 2))
    unit_price = Column(Numeric(15, 2))
    total_price = Column(Numeric(15, 2))
    checked = Column(Boolean, default=False)
    category = relationship("ExpenseCategory", back_populates="modules")

# 以下是 Skill 要求的关联模型
class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    company = Column(String(200))
    name = Column(String(100))
    phone = Column(String(50))
    email = Column(String(200))
    address = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

class Quotation(Base):
    __tablename__ = "quotations"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    client_id = Column(Integer, ForeignKey("clients.id"))
    quotation_number = Column(String(100), unique=True)
    title = Column(String(200))
    tax_rate = Column(Numeric(5, 4), default=0.0600)
    discount = Column(Numeric(5, 4), default=1.0000)
    total_amount = Column(Numeric(15, 2), default=0)
    status = Column(String(50), default="draft")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    project = relationship("Project")
    client = relationship("Client")

class QuotationVersion(Base):
    __tablename__ = "quotation_versions"
    id = Column(Integer, primary_key=True, index=True)
    quotation_id = Column(Integer, ForeignKey("quotations.id"))
    version_number = Column(Integer)
    changes = Column(Text)
    total_amount = Column(Numeric(15, 2))
    created_at = Column(DateTime, default=datetime.now)
