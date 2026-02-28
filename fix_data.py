import sqlite3
import os

db_path = r'D:\wwwroot\quotation_system\data\quotation.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 修复 Project 表的空值
    cursor.execute("UPDATE projects SET status = 'draft' WHERE status IS NULL")
    cursor.execute("UPDATE projects SET tax_rate = 0.06 WHERE tax_rate IS NULL")
    cursor.execute("UPDATE projects SET discount = 1.0 WHERE discount IS NULL")
    cursor.execute("UPDATE projects SET development_total = 0 WHERE development_total IS NULL")
    cursor.execute("UPDATE projects SET other_costs_total = 0 WHERE other_costs_total IS NULL")
    
    # 修复 FunctionModule 表的空值
    cursor.execute("UPDATE function_modules SET checked = 0 WHERE checked IS NULL")
    cursor.execute("UPDATE function_modules SET work_months = 0 WHERE work_months IS NULL")
    cursor.execute("UPDATE function_modules SET unit_price = 15000 WHERE unit_price IS NULL")
    cursor.execute("UPDATE function_modules SET total_price = 0 WHERE total_price IS NULL")
    
    conn.commit()
    print("数据库默认值已修复")
    conn.close()
else:
    print("数据库文件未找到")
