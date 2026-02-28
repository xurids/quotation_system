from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any
from decimal import Decimal
from datetime import datetime

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class FunctionModuleBase(BaseSchema):
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

class FunctionModuleCreate(FunctionModuleBase):
    category_id: int

class FunctionModule(FunctionModuleBase):
    id: int
    category_id: int

class ExpenseCategoryBase(BaseSchema):
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    budget_amount: Optional[Decimal] = Field(default=Decimal('0'))
    sort_order: int = 0

class ExpenseCategoryCreate(ExpenseCategoryBase):
    project_id: int

class ExpenseCategory(ExpenseCategoryBase):
    id: int
    project_id: int
    modules: List[FunctionModule] = []

class OtherCostBase(BaseSchema):
    cost_type: str
    cost_name: str
    description: Optional[str] = None
    cost_amount: Decimal = Field(default=Decimal('0'))
    calculation_rule: Optional[str] = None
    is_fixed: bool = False
    fixed_amount: Optional[Decimal] = None

class OtherCostCreate(OtherCostBase):
    project_id: int

class OtherCost(OtherCostBase):
    id: int
    project_id: int

class ProjectBase(BaseSchema):
    name: str
    code: Optional[str] = None
    total_budget: Optional[Decimal] = Field(default=Decimal('0'))
    development_total: Optional[Decimal] = Field(default=Decimal('0'))
    other_costs_total: Optional[Decimal] = Field(default=Decimal('0'))

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    created_at: datetime

class ProjectDetail(Project):
    categories: List[ExpenseCategory] = []
    other_costs: List[OtherCost] = []

class ClientBase(BaseSchema):
    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    address: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class Client(BaseSchema):
    id: int
    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime

class QuotationTemplateBase(BaseSchema):
    name: str
    description: Optional[str] = None
    content: Optional[str] = None

class QuotationTemplateCreate(QuotationTemplateBase):
    pass

class QuotationTemplate(QuotationTemplateBase):
    id: int
    created_at: datetime

class QuotationItemBase(BaseSchema):
    description: str
    quantity: Decimal = Field(default=Decimal('1'))
    unit_price: Decimal
    total_price: Decimal

class QuotationItemCreate(QuotationItemBase):
    pass

class QuotationItem(QuotationItemBase):
    id: int
    quotation_id: int

class QuotationBase(BaseSchema):
    project_id: int
    client_id: int
    template_id: Optional[int] = None
    quotation_number: str
    title: str
    description: Optional[str] = None
    tax_rate: Decimal = Field(default=Decimal('0'))
    discount: Decimal = Field(default=Decimal('0'))
    valid_until: Optional[datetime] = None
    status: Optional[str] = "draft"
    total_amount: Decimal = Field(default=Decimal('0'))

class QuotationCreate(QuotationBase):
    items: List[QuotationItemCreate] = []

class Quotation(QuotationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    items: List[QuotationItem] = []
    
class QuotationVersion(BaseSchema):
    id: int
    quotation_id: int
    version_number: int
    changes: str
    total_amount: Decimal
    created_at: datetime
