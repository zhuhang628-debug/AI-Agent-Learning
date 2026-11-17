
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import services
from database import get_db
from schemas import UserCreate, UserUpdate, UserResponse

router = APIRouter(
    prefix="/users",
    tags=["用户管理"]
)


# 创建用户
@router.post("/", response_model=UserResponse)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    try:
        return services.register_user(db, user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# 查询所有用户
@router.get("/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return services.list_users(db)


# 查询单个用户
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    try:
        return services.get_user(db, user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# 修改用户
@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    try:
        return services.modify_user(db, user_id, user_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# 删除用户
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    try:
        services.remove_user(db, user_id)
        return {"message": "用户删除成功"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
