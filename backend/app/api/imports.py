from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models import FunctionModule, ExpenseCategory, Project
from decimal import Decimal
import pandas as pd
from io import BytesIO
from typing import Optional
import re
import datetime
import uuid

router = APIRouter()

def log(msg):
    print(f"DEBUG [{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def safe_decimal(val):
    """极致安全的数字转换，处理空值、横线、NaN"""
    try:
        if pd.isna(val) or val is None: return Decimal('0')
        s = str(val).strip()
        if not s or s.lower() in ['nan', 'none', '-', '']: return Decimal('0')
        # 移除非数字符号 (保留小数点)
        clean = re.sub(r'[^\d.-]', '', s)
        return Decimal(clean) if clean else Decimal('0')
    except:
        return Decimal('0')

@router.post("/import-excel")
async def import_excel_modules(file: UploadFile = File(...), project_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    log(f"🚀 启动导入: {file.filename}")
    try:
        contents = await file.read()
        all_sheets = pd.read_excel(BytesIO(contents), sheet_name=None, header=None)
        sheet_name = max(all_sheets, key=lambda k: len(all_sheets[k]))
        df = all_sheets[sheet_name]
        
        if not project_id:
            project = Project(name=f"新项目_{datetime.datetime.now().strftime('%m%d%H%M')}", code=f"PROJ-{uuid.uuid4().hex[:6].upper()}")
            db.add(project); db.flush(); project_id = project.id
        else:
            project = db.query(Project).filter(Project.id == project_id).first()

        # 寻找表头所在行
        header_row, wm_col, pr_col = -1, 9, 10
        for i, row in df.iterrows():
            txt = "".join([str(x) for x in row.values if not pd.isna(x)])
            if any(k in txt for k in ["人月", "工作量", "单价"]):
                header_row = i
                for c_idx, cell in enumerate(row.values):
                    v = str(cell)
                    if any(k in v for k in ["人月", "工作量"]): wm_col = c_idx
                    if any(k in v for k in ["单价", "价格", "元"]) and "总价" not in v: pr_col = c_idx
                break
        
        log(f"📍 命中表头: 第 {header_row+1} 行")

        count = 0
        last = [""] * 15 # 层级记忆
        category_cache = {}

        for i in range(header_row + 1, len(df)):
            row = df.iloc[i]
            def get_v(c_idx):
                if c_idx >= len(row): return ""
                v = row[c_idx]
                return str(v).strip() if not pd.isna(v) and str(v).lower() != 'nan' else ""

            wm = safe_decimal(row[wm_col] if wm_col < len(row) else 0)
            up = safe_decimal(row[pr_col] if pr_col < len(row) else 0)
            
            # 跳过空行和小计行
            if wm == 0 and up == 0 and not get_v(1): continue
            line_text = "".join([get_v(j) for j in range(min(10, len(row)))])
            if any(k in line_text for k in ["小计", "合计", "TOTAL"]): continue

            # 更新记忆
            for j in range(1, 8):
                v = get_v(j)
                if v: last[j] = v
            
            if not any(last[1:8]): continue # 没有名称的行不入库

            # 确定分类
            cat_name = last[2] or last[1] or "业务开发费"
            if cat_name not in category_cache:
                cat = db.query(ExpenseCategory).filter(ExpenseCategory.project_id == project_id, ExpenseCategory.name == cat_name).first()
                if not cat:
                    cat = ExpenseCategory(name=cat_name, project_id=project_id)
                    db.add(cat); db.flush()
                category_cache[cat_name] = cat.id

            mod = FunctionModule(
                category_id=category_cache[cat_name], system_name=last[1], subsystem_name=last[2],
                level1=last[3], level2=last[4], level3=last[5],
                level4=get_v(6), level5=get_v(7), description=get_v(8),
                work_months=wm, unit_price=up, total_price=wm * up
            )
            db.add(mod); count += 1

        db.commit()
        log(f"✅ 完美导入 {count} 条功能点")
        return {"code": 0, "message": f"成功导入 {count} 条数据", "data": {"imported": count, "project_id": project_id}}
    except Exception as e:
        db.rollback()
        log(f"❌ 导入失败: {str(e)}")
        return {"code": 500, "message": f"服务器错误: {str(e)}"}
