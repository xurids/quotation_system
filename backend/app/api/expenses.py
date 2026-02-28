from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import FunctionModule, ExpenseCategory, Project
from decimal import Decimal
import traceback
import json

router = APIRouter()

@router.get("/projects/{project_id}/summary")
def get_project_summary(project_id: int, db: Session = Depends(get_db)):
    print(f"--- 诊断开始: 获取项目 {project_id} 的概算汇总 ---")
    try:
        # 1. 检查项目是否存在
        proj = db.query(Project).filter(Project.id == project_id).first()
        if not proj:
            return {"code": 1, "msg": "项目不存在"}

        # 2. 获取分类
        categories = db.query(ExpenseCategory).filter(ExpenseCategory.project_id == project_id).all()
        summary_data = {"categories": []}
        
        for cat in categories:
            # 3. 获取模块
            modules = db.query(FunctionModule).filter(FunctionModule.category_id == cat.id).all()
            mod_list = []
            for m in modules:
                try:
                    # 安全地提取名称，防止字段缺失
                    display_name = getattr(m, 'level5', None) or getattr(m, 'level4', None) or \
                                   getattr(m, 'level3', None) or getattr(m, 'level2', None) or \
                                   getattr(m, 'level1', None) or getattr(m, 'system_name', None) or "未命名功能"
                    
                    mod_list.append({
                        "id": m.id, 
                        "name": display_name,
                        "system_name": m.system_name, 
                        "subsystem_name": m.subsystem_name,
                        "level1": m.level1, 
                        "level2": m.level2, 
                        "level3": m.level3,
                        "level4": m.level4, 
                        "level5": m.level5,
                        "description": m.description, 
                        "work_months": float(m.work_months or 0),
                        "unit_price": float(m.unit_price or 0), 
                        "total_price": float(m.total_price or 0),
                        "checked": bool(m.checked)
                    })
                except Exception as mod_err:
                    print(f"模块数据处理错误 (ID: {getattr(m, 'id', 'unknown')}): {str(mod_err)}")
                    continue
            
            summary_data["categories"].append({
                "id": cat.id, 
                "name": cat.name,
                "modules": mod_list
            })
        
        print(f"--- 诊断成功: 返回了 {len(summary_data['categories'])} 个类别 ---")
        return {"code": 0, "data": summary_data}
        
    except Exception as e:
        print(f"!!! 严重错误 !!!: {str(e)}")
        traceback.print_exc()
        # 将错误详情直接返回给前端，方便排查
        return {
            "code": 500, 
            "msg": "后端执行异常", 
            "detail": str(e),
            "traceback": traceback.format_exc()
        }
