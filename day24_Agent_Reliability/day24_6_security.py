
from pydantic import BaseModel, Field, field_validator
from langchain.tools import tool


# ==============================
# 1. 定义工具输入参数
# ==============================

class OrderInput(BaseModel):

    order_no: str = Field(
        description="订单编号"
    )

    @field_validator("order_no")
    @classmethod
    def validate_order_no(cls, value):

        value = value.strip()

        if not value:
            raise ValueError("订单编号不能为空")

        if not value.startswith("A"):
            raise ValueError("订单编号必须以 A 开头")

        if not value[1:].isdigit():
            raise ValueError("订单编号格式不正确")

        return value


# ==============================
# 2. 模拟订单数据库
# ==============================

orders = {
    "A1001": {
        "order_no": "A1001",
        "user_id": "user1",
        "amount": 199.00,
        "status": "已发货"
    },

    "A1002": {
        "order_no": "A1002",
        "user_id": "user1",
        "amount": 299.00,
        "status": "待付款"
    },

    "A1003": {
        "order_no": "A1003",
        "user_id": "user2",
        "amount": 599.00,
        "status": "已完成"
    }
}


# ==============================
# 3. 模拟当前登录用户
# ==============================

CURRENT_USER_ID = "user1"


# ==============================
# 4. 定义安全查询工具
# ==============================

@tool(args_schema=OrderInput)
def query_order(order_no: str) -> dict:
    """
    根据订单编号查询当前登录用户自己的订单。
    """

    order = orders.get(order_no)

    if not order:
        return {
            "success": False,
            "message": "订单不存在"
        }

    # 权限校验
    if order["user_id"] != CURRENT_USER_ID:

        return {
            "success": False,
            "message": "无权查询该订单"
        }

    return {
        "success": True,
        "data": order
    }


# ==============================
# 5. 测试安全机制
# ==============================

def main():

    test_cases = [
        ("A1001", "正常查询"),
        ("A1003", "查询其他用户订单"),
        ("B1001", "非法订单编号"),
        ("", "空订单编号"),
        ("A9999", "查询不存在的订单")
    ]

    for order_no, description in test_cases:

        print(f"\n========== {description} ==========")

        try:

            result = query_order.invoke({
                "order_no": order_no
            })

            print("查询结果：", result)

        except Exception as e:

            print("参数校验失败：", str(e))


if __name__ == "__main__":
    main()
