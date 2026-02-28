from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from typing import List, Optional
from ..database import get_db
from ..models import Project, ExpenseCategory, FunctionModule, Quotation, QuotationVersion, Client
from ..schemas import QuotationBase
from decimal import Decimal
import datetime
import uuid

router = APIRouter()

@router.get("")
@router.get("/")
def list_quotations(
    q: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    query = db.query(Quotation).options(
        joinedload(Quotation.project),
        joinedload(Quotation.client)
    )
    if q:
        query = query.filter(or_(Quotation.quotation_number.contains(q), Quotation.title.contains(q)))
    if status:
        query = query.filter(Quotation.status == status)
    
    total = query.count()
    results = query.order_by(Quotation.updated_at.desc()).offset((page-1)*size).limit(size).all()
    
    return {
        "code": 0,
        "data": {
            "list": results,
            "length": total,
            "pageNo": page,
            "pageSize": size
        }
    }


@router.post("/create-version/{project_id}")
def create_quotation_version(
    project_id: int, 
    data: dict = Body(...), 
    db: Session = Depends(get_db)
):
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")

        # Find or create quotation for this project
        quotation = db.query(Quotation).filter(Quotation.project_id == project_id).first()
        if not quotation:
            quotation = Quotation(
                project_id=project_id,
                client_id=data.get('client_id'),
                quotation_number=f"QT-{datetime.datetime.now().strftime('%Y%m%d%H%M')}-{uuid.uuid4().hex[:4].upper()}",
                title=f"{project.name} - 报价单",
                status="draft",
                tax_rate=Decimal(str(data.get('tax_rate', 0.06))),
                discount=Decimal(str(data.get('discount', 1.0))),
                total_amount=Decimal(str(data.get('total_amount', 0)))
            )
            db.add(quotation)
            db.flush()
        else:
            # Update existing quotation
            if data.get('client_id'): quotation.client_id = data.get('client_id')
            quotation.tax_rate = Decimal(str(data.get('tax_rate', 0.06)))
            quotation.discount = Decimal(str(data.get('discount', 1.0)))
            quotation.total_amount = Decimal(str(data.get('total_amount', 0)))
            quotation.updated_at = datetime.datetime.now()

        # Count existing versions
        v_count = db.query(QuotationVersion).filter(QuotationVersion.quotation_id == quotation.id).count()
        
        # Create version snapshot
        version = QuotationVersion(
            quotation_id=quotation.id,
            version_number=v_count + 1,
            changes=data.get('remark', '系统生成快照'),
            total_amount=Decimal(str(data.get('total_amount', 0))),
            created_at=datetime.datetime.now()
        )
        db.add(version)
        db.commit()
        
        return {"code": 0, "message": f"版本 V{version.version_number} 已成功归档", "data": {"version": version.version_number}}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{quotation_id}/versions")
def get_quotation_versions(quotation_id: int, db: Session = Depends(get_db)):
    versions = db.query(QuotationVersion).filter(QuotationVersion.quotation_id == quotation_id).order_by(QuotationVersion.version_number.desc()).all()
    return {"code": 0, "data": versions}
