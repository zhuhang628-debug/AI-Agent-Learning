
import asyncio
import logging
import time


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("TimeoutIntegration")


# 模拟一个执行缓慢的工具
async def slow_database_tool():

    logger.info("开始执行数据库查询")

    await asyncio.sleep(10)

    return "数据库查询成功"


# 带超时控制的工具调用
async def call_tool_with_timeout():

    try:
        result = await asyncio.wait_for(
            slow_database_tool(),
            timeout=3
        )

        return {
            "success": True,
            "data": result,
            "error": None
        }

    except asyncio.TimeoutError:

        logger.warning("数据库查询超时")

        return {
            "success": False,
            "data": None,
            "error": "工具执行超时，请稍后重试"
        }


async def main():

    print("=" * 45)
    print("Day24 Timeout 综合测试")
    print("=" * 45)

    start_time = time.perf_counter()

    result = await call_tool_with_timeout()

    elapsed = time.perf_counter() - start_time

    print("\n执行结果：")
    print(result)

    print(f"\n实际耗时：{elapsed:.2f} 秒")

    if not result["success"] and elapsed < 5:
        print("Timeout 测试通过！")
    else:
        print("Timeout 测试未通过！")


if __name__ == "__main__":
    asyncio.run(main())
