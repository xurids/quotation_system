from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
router = APIRouter()
@router.get("/projects/{project_id}/other-costs")
def list_other_costs(project_id: int, db: Session = Depends(get_db)): return {"code": 0, "data": []}
