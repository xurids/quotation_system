from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from ..database import get_db
from ..models import Project, ExpenseCategory, FunctionModule
from ..schemas import ProjectCreate
from decimal import Decimal
from fastapi.responses import StreamingResponse
from io import BytesIO
import pandas as pd
import datetime

router = APIRouter()

@router.get("/")
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    # 转换为 JSON 兼容格式
    data = []
    for p in projects:
        data.append({
            "id": p.id,
            "name": p.name,
            "code": p.code,
            "total_budget": float(p.total_budget or 0),
            "created_at": p.created_at
        })
    return {"code": 0, "data": data}

@router.post("/")
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """补全缺失的项目创建接口"""
    try:
        db_project = Project(
            name=project.name, 
            code=project.code or f"PROJ-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return {"code": 0, "message": "项目创建成功", "data": {"id": db_project.id}}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return {
        "code": 0, 
        "data": {
            "id": project.id,
            "name": project.name,
            "code": project.code,
            "total_budget": float(project.total_budget or 0)
        }
    }

@router.put("/{project_id}/batch-update")
def batch_update(project_id: int, modules: List[dict] = Body(...), db: Session = Depends(get_db)):
    try:
        for m in modules:
            db_mod = db.query(FunctionModule).filter(FunctionModule.id == m['id']).first()
            if db_mod:
                db_mod.work_months = Decimal(str(m['work_months']))
                db_mod.total_price = db_mod.work_months * db_mod.unit_price
        db.commit()
        return {"code": 0, "message": "修改已保存"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{project_id}/export-excel")
def export_excel(project_id: int, selected_ids: List[int] = Body(...), db: Session = Depends(get_db)):
    modules = db.query(FunctionModule).filter(FunctionModule.id.in_(selected_ids)).all()
    rows = []
    for i, m in enumerate(modules, 1):
        rows.append({
            "序号": i, "系统": m.system_name, "子系统": m.subsystem_name,
            "一级": m.level1, "二级": m.level2, "三级": m.level3,
            "说明": m.description, "人月": float(m.work_months),
            "单价": float(m.unit_price), "总价": float(m.total_price)
        })
    df = pd.DataFrame(rows)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='概算')
    output.seek(0)
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    p = db.query(Project).filter(Project.id == project_id).first()
    if p:
        db.delete(p)
        db.commit()
    return {"code": 0, "message": "项目已删除"}
