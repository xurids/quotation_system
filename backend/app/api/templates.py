from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import QuotationTemplate
from ..schemas import QuotationTemplate as QuotationTemplateSchema

router = APIRouter()

@router.get("/")
def list_templates(db: Session = Depends(get_db)):
    templates = db.query(QuotationTemplate).all()
    return {"code": 0, "data": templates}

@router.get("/{template_id}")
def get_template(template_id: int, db: Session = Depends(get_db)):
    template = db.query(QuotationTemplate).filter(QuotationTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    return {"code": 0, "data": template}
