
from pydantic import BaseModel, Field, EmailStr


# 用户注册请求
class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    age: int = Field(ge=1, le=120)
    password: str = Field(min_length=6, max_length=128)


# 用户登录请求
class UserLogin(BaseModel):
    username: str
    password: str


# Token 响应
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

