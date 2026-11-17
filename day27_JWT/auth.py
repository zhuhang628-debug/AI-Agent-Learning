
from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)
from sqlalchemy.orm import Session
from jwt.exceptions import InvalidTokenError

from database import get_db
from models import User
from schemas import UserRegister, UserLogin, TokenResponse

from security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token
)


router = APIRouter(
    prefix="/auth",
    tags=["身份认证"]
)

# 从请求头提取 Bearer Token
bearer_scheme = HTTPBearer()


# =====================================
# 1. 用户注册
# =====================================
@router.post("/register")
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    # 检查用户名
    existing_user = db.query(User).filter(
        User.username == user_data.username
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="用户名已经存在"
        )

    # 检查邮箱
    existing_email = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="邮箱已经注册"
        )

    # 密码哈希
    hashed_password = get_password_hash(
        user_data.password
    )

    # 创建用户
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        age=user_data.age,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "注册成功",
        "user_id": new_user.id,
        "username": new_user.username
    }


# =====================================
# 2. 用户登录
# =====================================
@router.post("/login", response_model=TokenResponse)
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    # 查询用户
    user = db.query(User).filter(
        User.username == user_data.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="用户名或密码错误"
        )

    # 验证密码
    if not user.hashed_password or not verify_password(
        user_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="用户名或密码错误"
        )

    # 生成 JWT
    access_token = create_access_token({
        "sub": str(user.id)
    })

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# =====================================
# 3. 获取当前登录用户
# =====================================
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="身份认证失败，请重新登录",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        # 获取 Token
        token = credentials.credentials

        # 验证 JWT
        payload = decode_access_token(token)

        # 获取用户 ID
        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)

    except (InvalidTokenError, ValueError, TypeError):
        raise credentials_exception

    # 根据 ID 查询用户
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None:
        raise credentials_exception

    return user


# =====================================
# 4. 获取当前用户信息（受保护接口）
# =====================================
@router.get("/me")
def get_my_info(
    current_user: User = Depends(get_current_user)
):
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "age": current_user.age
    }
# =====================================
# 5. 用户数据隔离（权限控制）
# =====================================
@router.get("/users/{user_id}")
def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    # 判断请求的用户 ID 是否属于当前登录用户
    if user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="无权访问其他用户的数据"
        )

    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "age": current_user.age
    }