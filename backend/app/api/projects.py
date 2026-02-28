from fastapi import APIRouter, Depends, HTTPException, Body, Query, Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from typing import List, Optional
from ..database import get_db
from ..models import Project, ExpenseCategory, FunctionModule, Client
from ..schemas import ProjectCreate
from decimal import Decimal
from fastapi.responses import StreamingResponse
from io import BytesIO
import pandas as pd
import datetime

router = APIRouter()

@router.get("")
@router.get("/")
def list_projects(
    q: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    # 打印日志到终端，方便确认是否进入了此函数
    print(f"--- 触发分页接口 v3 --- Params: q={q}, status={status}, page={page}, size={size}")
    
    query = db.query(Project).options(joinedload(Project.client))
    
    if q and q.strip():
        query = query.filter(or_(Project.name.contains(q), Project.code.contains(q)))
    if status and status.strip():
        query = query.filter(Project.status == status)
    
    total = query.count()
    projects = query.order_by(Project.created_at.desc()).offset((page - 1) * size).limit(size).all()
    
    project_list = []
    for p in projects:
        project_list.append({
            "id": p.id,
            "name": p.name,
            "code": p.code,
            "status": p.status or "draft",
            "tax_rate": float(p.tax_rate or 0.06),
            "discount": float(p.discount or 1.0),
            "total_budget": float(p.total_budget or 0),
            "created_at": p.created_at,
            "client_name": p.client.company if p.client else "未关联"
        })
    
    # 强制返回包含 list 等字段的结构
    result = {
        "code": 0,
        "msg": "success",
        "version_tag": "FORCE_PAGINATION_v3",
        "data": {
            "list": project_list,
            "length": total,
            "pageNo": page,
            "pageSize": size
        }
    }
    return result

@router.post("")
@router.post("/")
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    try:
        db_project = Project(
            name=project.name, 
            code=project.code or f"PROJ-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            status="draft",
            tax_rate=Decimal("0.06"),
            discount=Decimal("1.0")
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
            "client_id": project.client_id,
            "status": project.status or "draft",
            "tax_rate": float(project.tax_rate or 0.06),
            "discount": float(project.discount or 1.0),
            "total_budget": float(project.total_budget or 0)
        }
    }

@router.put("/{project_id}")
def update_project(project_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    fields = ['name', 'client_id', 'status', 'tax_rate', 'discount']
    for field in fields:
        if field in data:
            val = data[field]
            if field in ['tax_rate', 'discount'] and val is not None:
                val = Decimal(str(val))
            setattr(db_project, field, val)
    
    # 重新计算总预算
    all_checked_modules = db.query(FunctionModule).join(ExpenseCategory).filter(
        ExpenseCategory.project_id == project_id, 
        FunctionModule.checked == True
    ).all()
    dev_total = sum([m.total_price for m in all_checked_modules])
    db_project.development_total = dev_total
    db_project.total_budget = dev_total * (1 + (db_project.tax_rate or Decimal("0.06"))) * (db_project.discount or Decimal("1.0"))
    
    db.commit()
    return {"code": 0, "message": "更新成功", "total_budget": float(db_project.total_budget)}

@router.put("/{project_id}/batch-update")
def batch_update(project_id: int, modules: List[dict] = Body(...), db: Session = Depends(get_db)):
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        for m in modules:
            db_mod = db.query(FunctionModule).filter(FunctionModule.id == m['id']).first()
            if db_mod:
                db_mod.work_months = Decimal(str(m.get('work_months', 0)))
                db_mod.unit_price = Decimal(str(m.get('unit_price', 0)))
                db_mod.checked = m.get('checked', False)
                db_mod.total_price = db_mod.work_months * db_mod.unit_price
        
        all_checked_modules = db.query(FunctionModule).join(ExpenseCategory).filter(
            ExpenseCategory.project_id == project_id, 
            FunctionModule.checked == True
        ).all()
        dev_total = sum([m.total_price for m in all_checked_modules])
        project.development_total = dev_total
        project.total_budget = dev_total * (1 + (project.tax_rate or Decimal("0.06"))) * (project.discount or Decimal("1.0"))
        
        db.commit()
        return {"code": 0, "message": "修改已保存", "total_budget": float(project.total_budget)}
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
