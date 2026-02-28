from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from ..database import get_db
from ..models import Project, ExpenseCategory, FunctionModule, Quotation, QuotationVersion, Client
from ..schemas import QuotationBase
from decimal import Decimal
import datetime
import uuid

router = APIRouter()

@router.get("/")
def list_quotations(db: Session = Depends(get_db)):
    # Join with Project and Client to get names
    results = db.query(Quotation).all()
    # Pydantic models will handle the serialization if relationships are loaded
    return {"code": 0, "data": results}

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
                total_amount=Decimal(str(data.get('total_amount', 0)))
            )
            db.add(quotation)
            db.flush()
        else:
            # Update existing quotation status and amount
            if data.get('client_id'):
                quotation.client_id = data.get('client_id')
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
