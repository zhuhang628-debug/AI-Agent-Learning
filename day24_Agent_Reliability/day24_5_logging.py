
import logging
import time
from pathlib import Path


# ==============================
# 1. 创建日志目录
# ==============================

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"

LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "agent.log"


# ==============================
# 2. 配置日志
# ==============================

logging.basicConfig(
    level=logging.INFO,

    format=(
        "%(asctime)s - "
        "%(name)s - "
        "%(levelname)s - "
        "%(message)s"
    ),

    handlers=[
        logging.FileHandler(
            LOG_FILE,
            encoding="utf-8"
        ),

        logging.StreamHandler()
    ],

    force=True
)

logger = logging.getLogger("Agent")


# ==============================
# 3. 模拟订单查询节点
# ==============================

def query_order(order_no: str):

    logger.info(f"开始查询订单：{order_no}")

    time.sleep(1)

    if order_no == "A9999":
        raise ValueError("订单不存在")

    result = {
        "order_no": order_no,
        "amount": 199.00,
        "status": "已发货"
    }

    logger.info(f"订单查询成功：{order_no}")

    return result


# ==============================
# 4. 模拟 Agent 分析节点
# ==============================

def analyze_order(order_data: dict):

    logger.info("开始执行订单分析")

    time.sleep(1)

    result = (
        f"订单 {order_data['order_no']} "
        f"金额为 {order_data['amount']} 元，"
        f"当前状态为 {order_data['status']}。"
    )

    logger.info("订单分析完成")

    return result


# ==============================
# 5. 记录完整执行过程
# ==============================

def run_agent(order_no: str):

    start_time = time.time()

    logger.info("========== Agent 开始执行 ==========")

    try:

        order_data = query_order(order_no)

        analysis = analyze_order(order_data)

        logger.info("Agent 执行成功")

        print("\n分析结果：")
        print(analysis)

    except Exception:

        logger.exception("Agent 执行失败")

        print("\nAgent 执行失败，请检查日志")

    finally:

        elapsed = time.time() - start_time

        logger.info(
            f"Agent 执行结束，总耗时：{elapsed:.2f} 秒"
        )


# ==============================
# 6. 主程序
# ==============================

if __name__ == "__main__":

    run_agent("A1001")

    print("\n========== 测试异常订单 ==========")

    run_agent("A9999")
