
import asyncio
from enum import Enum


# ==============================
# 1. 定义异常类型
# ==============================

class ErrorType(Enum):

    PARAMETER_ERROR = "参数错误"
    BUSINESS_ERROR = "业务错误"
    TIMEOUT_ERROR = "超时错误"
    SYSTEM_ERROR = "系统错误"


# ==============================
# 2. 定义自定义异常
# ==============================

class AgentException(Exception):

    def __init__(self, error_type: ErrorType, message: str):

        self.error_type = error_type
        self.message = message

        super().__init__(message)


# ==============================
# 3. 模拟订单查询
# ==============================

async def query_order(order_no: str):

    if not order_no:
        raise AgentException(
            ErrorType.PARAMETER_ERROR,
            "订单编号不能为空"
        )

    if order_no == "A9999":
        raise AgentException(
            ErrorType.BUSINESS_ERROR,
            "没有找到该订单"
        )

    if order_no == "TIMEOUT":
        await asyncio.sleep(5)

    if order_no == "ERROR":
        raise RuntimeError("数据库连接失败")

    return {
        "order_no": order_no,
        "amount": 199.00,
        "status": "已发货"
    }


# ==============================
# 4. 统一异常处理
# ==============================

async def handle_order(order_no: str):

    try:

        result = await asyncio.wait_for(
            query_order(order_no),
            timeout=2
        )

        return {
            "success": True,
            "data": result,
            "error_type": None,
            "message": "订单查询成功"
        }

    except AgentException as e:

        return {
            "success": False,
            "data": None,
            "error_type": e.error_type.value,
            "message": e.message
        }

    except asyncio.TimeoutError:

        return {
            "success": False,
            "data": None,
            "error_type": ErrorType.TIMEOUT_ERROR.value,
            "message": "订单查询超时，请稍后重试"
        }

    except Exception as e:

        return {
            "success": False,
            "data": None,
            "error_type": ErrorType.SYSTEM_ERROR.value,
            "message": "系统暂时无法处理请求"
        }


# ==============================
# 5. 测试不同异常场景
# ==============================

async def main():

    test_cases = [
        ("A1001", "正常订单"),
        ("", "空订单编号"),
        ("A9999", "订单不存在"),
        ("TIMEOUT", "模拟超时"),
        ("ERROR", "模拟系统异常")
    ]

    for order_no, description in test_cases:

        print(f"\n========== {description} ==========")

        result = await handle_order(order_no)

        print("处理结果：", result)


if __name__ == "__main__":
    asyncio.run(main())
