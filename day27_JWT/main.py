
import sys
from pathlib import Path

from fastapi import FastAPI

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
DAY26_DIR = PROJECT_ROOT / "day26_MySQL"

# Day27 优先，Day26 作为共享数据库模块
sys.path.insert(0, str(DAY26_DIR))
sys.path.insert(0, str(BASE_DIR))

from auth import router as auth_router


app = FastAPI(
    title="Day27 JWT Authentication",
    description="用户注册、登录与 JWT 身份认证",
    version="1.0.0"
)

app.include_router(auth_router)


@app.get("/health", tags=["健康检查"])
def health():
    return {"status": "ok"}
