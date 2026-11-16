
import logging
import pymysql

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)


# ==============================
# 1. 日志配置
# ==============================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("RetryIntegration")


# ==============================
# 2. 模拟数据库连接
# ==============================

attempt_count = 0


def mock_mysql_connection():

    global attempt_count
    attempt_count += 1

    logger.info("正在尝试连接 MySQL，第 %s 次", attempt_count)

    # 前两次模拟连接失败
    if attempt_count <= 2:
        raise pymysql.OperationalError(
            2003,
            "模拟 MySQL 连接失败"
        )

    # 第三次连接成功
    return "MySQL 数据库连接成功！"


# ==============================
# 3. 配置 Retry
# ==============================

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(
        multiplier=1,
        min=1,
        max=4
    ),
    retry=retry_if_exception_type(
        pymysql.OperationalError
    ),
    before_sleep=before_sleep_log(
        logger,
        logging.WARNING
    ),
    reraise=True
)
def query_mysql_with_retry():

    return mock_mysql_connection()


# ==============================
# 4. 测试入口
# ==============================

def main():

    print("=" * 45)
    print("Day24 Retry 综合测试")
    print("=" * 45)

    try:
        result = query_mysql_with_retry()

        print("\n最终执行结果：")
        print(result)

        print(f"\n总尝试次数：{attempt_count}")

        if attempt_count == 3:
            print("Retry 测试通过！")

    except pymysql.OperationalError as e:

        print("\n数据库连接最终失败：")
        print(e)

        print(f"总尝试次数：{attempt_count}")


if __name__ == "__main__":
    main()
