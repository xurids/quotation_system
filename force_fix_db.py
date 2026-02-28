import sqlite3
import os

db_path = r'D:\wwwroot\quotation_system\data\quotation.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取现有列
    cursor.execute("PRAGMA table_info(projects)")
    columns = [row[1] for row in cursor.fetchall()]
    
    # 手动添加缺失字段
    if 'status' not in columns:
        cursor.execute("ALTER TABLE projects ADD COLUMN status VARCHAR(50) DEFAULT 'draft'")
    if 'tax_rate' not in columns:
        cursor.execute("ALTER TABLE projects ADD COLUMN tax_rate NUMERIC(5, 4) DEFAULT 0.0600")
    if 'discount' not in columns:
        cursor.execute("ALTER TABLE projects ADD COLUMN discount NUMERIC(5, 4) DEFAULT 1.0000")
    if 'client_id' not in columns:
        cursor.execute("ALTER TABLE projects ADD COLUMN client_id INTEGER REFERENCES clients(id)")

    # 修复模块表
    cursor.execute("PRAGMA table_info(function_modules)")
    mod_columns = [row[1] for row in cursor.fetchall()]
    if 'checked' not in mod_columns:
        cursor.execute("ALTER TABLE function_modules ADD COLUMN checked BOOLEAN DEFAULT 0")

    conn.commit()
    print("数据库字段已强制补全")
    conn.close()
else:
    print("数据库文件未找到")
