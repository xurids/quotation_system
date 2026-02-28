import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from backend.app.database import Base, engine
from backend.app.models import Project, ExpenseCategory, FunctionModule
from sqlalchemy.orm import Session

def init_database():
    print("🔧 正在同步数据库结构...")
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库同步完成")

if __name__ == "__main__":
    init_database()
