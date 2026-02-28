from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any
from decimal import Decimal
from datetime import datetime

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

# --- 客户相关 ---
class ClientBase(BaseSchema):
    company: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class Client(ClientBase):
    id: int
    created_at: datetime

# --- 项目相关 ---
class ProjectBase(BaseSchema):
    name: str
    code: Optional[str] = None
    client_id: Optional[int] = None
    status: Optional[str] = "draft"
    tax_rate: Optional[Decimal] = Field(default=Decimal('0.06'))
    discount: Optional[Decimal] = Field(default=Decimal('1.00'))
    total_budget: Optional[Decimal] = Field(default=Decimal('0'))
    development_total: Optional[Decimal] = Field(default=Decimal('0'))
    other_costs_total: Optional[Decimal] = Field(default=Decimal('0'))

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    created_at: datetime
    client_name: Optional[str] = None

# --- 功能模块相关 ---
class FunctionModuleBase(BaseSchema):
    id: Optional[int] = None
    system_name: Optional[str] = None
    subsystem_name: Optional[str] = None
    level1: Optional[str] = None
    level2: Optional[str] = None
    level3: Optional[str] = None
    level4: Optional[str] = None
    level5: Optional[str] = None
    description: Optional[str] = None
    work_months: Optional[Decimal] = Field(default=Decimal('0'))
    unit_price: Optional[Decimal] = Field(default=Decimal('15000'))
    total_price: Optional[Decimal] = Field(default=Decimal('0'))
    checked: Optional[bool] = False

class FunctionModule(FunctionModuleBase):
    id: int
    category_id: int

class ExpenseCategory(BaseSchema):
    id: int
    project_id: int
    name: str
    budget_amount: Optional[Decimal] = Field(default=Decimal('0'))
    modules: List[FunctionModule] = []

class ProjectDetail(Project):
    categories: List[ExpenseCategory] = []

# --- 报价单相关 ---
class QuotationBase(BaseSchema):
    project_id: int
    client_id: Optional[int] = None
    quotation_number: str
    title: str
    tax_rate: Decimal = Field(default=Decimal('0.06'))
    discount: Decimal = Field(default=Decimal('1.00'))
    total_amount: Decimal = Field(default=Decimal('0'))
    status: str = "draft"

class Quotation(QuotationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    project: Optional[Project] = None
    client: Optional[Client] = None

class QuotationVersion(BaseSchema):
    id: int
    quotation_id: int
    version_number: int
    changes: Optional[str] = None
    total_amount: Decimal
    created_at: datetime

# --- 模板相关 ---
class QuotationTemplateBase(BaseSchema):
    name: str
    description: Optional[str] = None
    content: Optional[str] = None

class QuotationTemplateCreate(QuotationTemplateBase):
    pass

class QuotationTemplate(QuotationTemplateBase):
    id: int
    created_at: datetime
