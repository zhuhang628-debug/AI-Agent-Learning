
from pydantic import BaseModel, Field, ConfigDict


# 创建用户时接收的数据
class UserCreate(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    email: str
    age: int = Field(ge=1, le=120)


# 修改用户时接收的数据
class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=2, max_length=50)
    email: str | None = None
    age: int | None = Field(default=None, ge=1, le=120)


# 返回给客户端的用户数据
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    age: int

    # 允许 Pydantic 从 ORM 对象读取属性
    model_config = ConfigDict(from_attributes=True)
