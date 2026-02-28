@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║         📦 项目经费预算报价系统 (恢复版)               ║
echo ║         一键启动 - 数据库 / 后端 / 前端                ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

:: 1. 检查并同步数据库
echo [1/3] 🔧 正在准备数据库...
python init_db.py

:: 2. 启动后端 (更换端口至 8899)
echo [2/3] 🚀 正在启动后端 API (Port: 8899)...
start "报价系统 - 后端" cmd /k "cd /d "%~dp0backend" && python -m pip install -r requirements.txt && uvicorn app.main:app --reload --port 8899 --host 0.0.0.0"

:: 3. 启动前端
echo [3/3] 🎨 正在启动前端界面...
start "报价系统 - 前端" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ✅ 系统启动指令已发出，端口已改为 8899，请稍候...
pause
