
from sqlalchemy.orm import Session

from models import User
from schemas import UserCreate, UserUpdate


# 创建用户
def create_user(db: Session, user_data: UserCreate):
    user = User(
        username=user_data.username,
        email=user_data.email,
        age=user_data.age
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# 查询所有用户
def get_users(db: Session):
    return db.query(User).order_by(User.id).all()


# 根据 ID 查询用户
def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


# 修改用户
def update_user(db: Session, user: User, user_data: UserUpdate):
    update_data = user_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    return user


# 删除用户
def delete_user(db: Session, user: User):
    db.delete(user)
    db.commit()
