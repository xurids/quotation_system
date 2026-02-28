import sqlite3
import os

db_path = r'D:\wwwroot\quotation_system\data\quotation.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 强制将所有 NULL 状态改为 draft
    cursor.execute("UPDATE projects SET status = 'draft' WHERE status IS NULL OR status = ''")
    cursor.execute("UPDATE projects SET tax_rate = 0.06 WHERE tax_rate IS NULL")
    cursor.execute("UPDATE projects SET discount = 1.0 WHERE discount IS NULL")
    
    # 报价单表也需要修复
    cursor.execute("PRAGMA table_info(quotations)")
    q_cols = [row[1] for row in cursor.fetchall()]
    if 'status' in q_cols:
        cursor.execute("UPDATE quotations SET status = 'draft' WHERE status IS NULL OR status = ''")
    if 'tax_rate' in q_cols:
        cursor.execute("UPDATE quotations SET tax_rate = 0.06 WHERE tax_rate IS NULL")
    if 'discount' in q_cols:
        cursor.execute("UPDATE quotations SET discount = 1.0 WHERE discount IS NULL")

    conn.commit()
    print("数据库空值已强制清洗为默认值")
    conn.close()
