import requests
import time
import subprocess
import os
import sys

def verify():
    print("🚀 开始全系统自动化审计...")
    
    # 1. 检查数据库文件
    db_path = "data/quotation.db"
    if os.path.exists(db_path):
        print(f"✅ 数据库文件存在: {db_path}")
    else:
        print(f"❌ 数据库缺失，尝试运行初始化...")
        subprocess.run(["python", "init_db.py"], capture_output=True)

    # 2. 验证 API
    # 我们假设用户已经在运行 run.bat 启动了后端
    url = "http://127.0.0.1:8888/api/projects/"
    
    try:
        # 先试着创建一个项目
        test_project = {"name": "自动化审计项目", "code": f"VERIFY-{int(time.time())}"}
        post_res = requests.post(url, json=test_project, timeout=5)
        print(f"📡 创建项目测试: Status={post_res.status_code}, Body={post_res.text}")
        
        if post_res.status_code == 200:
            # 查一下列表
            list_res = requests.get(url, timeout=5)
            data = list_res.json()
            print(f"📡 列表查询测试: {len(data.get('data', []))} 个项目在库")
            
            if len(data.get('data', [])) > 0:
                print("🎉🎉🎉 后端数据链路 [全线通畅]！")
            else:
                print("⚠️ 列表为空，请检查数据库写入权限。")
        else:
            print("❌ 创建项目失败，后端逻辑可能有隐患。")
            
    except Exception as e:
        print(f"❌ 无法连接到 8888 端口: {str(e)}")
        print("💡 提示：请确保 run.bat 已启动且后端黑窗口显示 8888 端口。")

if __name__ == "__main__":
    verify()
