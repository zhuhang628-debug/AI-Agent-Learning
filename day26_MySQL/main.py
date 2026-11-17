
from fastapi import FastAPI

from routers.users import router as users_router

app = FastAPI(
    title="Day26 MySQL User API",
    description="FastAPI + SQLAlchemy + MySQL 用户管理系统",
    version="1.0.0"
)

app.include_router(users_router)


@app.get("/health")
def health():
    return {"status": "ok"}
