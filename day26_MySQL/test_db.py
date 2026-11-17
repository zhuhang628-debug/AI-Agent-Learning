
from sqlalchemy import text
from database import engine

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("MySQL 连接成功！")
        print("测试结果：", result.scalar())

except Exception as e:
    print("MySQL 连接失败：", e)

finally:
    engine.dispose()
