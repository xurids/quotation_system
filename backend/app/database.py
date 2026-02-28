from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from pathlib import Path

# 强制使用绝对路径锁定数据库位置
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_DIR = BASE_DIR / "data"
DB_FILE = DB_DIR / "quotation.db"

# 自动创建 data 目录
DB_DIR.mkdir(parents=True, exist_ok=True)

# SQLite 绝对路径连接
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_FILE.as_posix()}"

print(f"📦 数据库锁定路径: {DB_FILE}")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}, # SQLite 必加
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
