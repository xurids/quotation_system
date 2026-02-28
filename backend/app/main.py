from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
import time
import datetime
from .database import get_db
from .config import settings

app = FastAPI(title="项目经费预算报价系统")

# 强制日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    print(f"🌍 收到请求: {request.method} {request.url}", flush=True)
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"✅ 处理完成: {response.status_code} (用时: {process_time:.2f}s)", flush=True)
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health(): 
    return {"status": "ok", "time": str(datetime.datetime.now())}

from .api import clients, projects, expenses, quotations, templates, imports, other_costs

app.include_router(clients.router, prefix="/api/clients", tags=["clients"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(expenses.router, prefix="/api/expenses", tags=["expenses"])
app.include_router(quotations.router, prefix="/api/quotations", tags=["quotations"])
app.include_router(templates.router, prefix="/api/templates", tags=["templates"])
app.include_router(imports.router, prefix="/api/imports", tags=["imports"])
app.include_router(other_costs.router, prefix="/api/other_costs", tags=["other_costs"])

print("\n" + "="*50)
print("🚀 系统后端已就绪！监听端口: 8888")
print("="*50 + "\n")
