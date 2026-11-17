
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# 加载当前项目目录下的 .env 文件
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
load_dotenv(PROJECT_ROOT / ".env")

# 读取数据库配置
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# 检查必要配置，避免连接配置缺失
if not all([DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME]):
    raise ValueError("数据库配置不完整，请检查 .env 文件")

# 创建数据库连接引擎
DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
)

engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
    pool_pre_ping=True
)

# 创建数据库 Session 工厂
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

# ORM 模型基类
class Base(DeclarativeBase):
    pass

# FastAPI 依赖注入：为每个请求提供数据库 Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
