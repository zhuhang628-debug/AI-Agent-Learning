
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash


# 1. 加载项目根目录的 .env
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
load_dotenv(PROJECT_ROOT / ".env")


# 2. JWT 配置
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

if not SECRET_KEY:
    raise RuntimeError("请在项目根目录 .env 中配置 JWT_SECRET_KEY")


# 3. 初始化密码哈希工具
password_hash = PasswordHash.recommended()


# 4. 密码哈希
def get_password_hash(password: str) -> str:
    """将明文密码转换为安全哈希"""
    return password_hash.hash(password)


# 5. 验证密码
def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """验证明文密码是否与数据库中的哈希匹配"""
    return password_hash.verify(plain_password, hashed_password)


# 6. 生成 JWT
def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None
) -> str:
    """生成 JWT Access Token"""

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({"exp": expire})

    token = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


# 7. 解码并验证 JWT
def decode_access_token(token: str) -> dict:
    """验证 JWT 签名和有效期，返回 Payload"""

    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM]
    )

    return payload
