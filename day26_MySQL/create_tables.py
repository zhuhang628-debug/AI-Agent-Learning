
from database import engine, Base
from models import User

# 根据 ORM 模型创建数据库表
Base.metadata.create_all(bind=engine)

print("数据表创建成功！")
