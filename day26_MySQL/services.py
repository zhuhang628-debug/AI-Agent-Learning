
from sqlalchemy.orm import Session

import crud
from schemas import UserCreate, UserUpdate


# 注册用户
def register_user(db: Session, user_data: UserCreate):
    users = crud.get_users(db)

    for user in users:
        if user.username == user_data.username:
            raise ValueError("用户名已存在")

        if user.email == user_data.email:
            raise ValueError("邮箱已存在")

    return crud.create_user(db, user_data)


# 查询所有用户
def list_users(db: Session):
    return crud.get_users(db)


# 获取指定用户
def get_user(db: Session, user_id: int):
    user = crud.get_user_by_id(db, user_id)

    if not user:
        raise ValueError("用户不存在")

    return user


# 修改用户
def modify_user(db: Session, user_id: int, user_data: UserUpdate):
    user = get_user(db, user_id)

    return crud.update_user(db, user, user_data)


# 删除用户
def remove_user(db: Session, user_id: int):
    user = get_user(db, user_id)

    crud.delete_user(db, user)
