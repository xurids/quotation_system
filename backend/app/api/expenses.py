from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import FunctionModule, ExpenseCategory, Project
from decimal import Decimal

router = APIRouter()

@router.get("/projects/{project_id}/summary")
def get_project_summary(project_id: int, db: Session = Depends(get_db)):
    categories = db.query(ExpenseCategory).filter(ExpenseCategory.project_id == project_id).all()
    summary_data = {"categories": []}
    for cat in categories:
        modules = db.query(FunctionModule).filter(FunctionModule.category_id == cat.id).all()
        summary_data["categories"].append({
            "id": cat.id, "name": cat.name,
            "modules": [{
                "id": m.id, "name": m.level5 or m.level4 or m.level3 or m.name,
                "system_name": m.system_name, "subsystem_name": m.subsystem_name,
                "level1": m.level1, "level2": m.level2, "level3": m.level3,
                "level4": m.level4, "level5": m.level5,
                "description": m.description, "work_months": float(m.work_months),
                "unit_price": float(m.unit_price), "total_price": float(m.total_price)
            } for m in modules]
        })
    return {"code": 0, "data": summary_data}
