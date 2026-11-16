
import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser


# ==================================
# 1. 加载环境变量
# ==================================

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR.parent / ".env")


# ==================================
# 2. 初始化 DeepSeek
# ==================================

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise ValueError("没有读取到 DEEPSEEK_API_KEY")

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=api_key,
    base_url="https://api.deepseek.com/v1",
    temperature=0
)


# ==================================
# 3. 定义结构化数据模型
# ==================================

class OrderAnalysis(BaseModel):

    order_no: str = Field(
        description="订单编号"
    )

    amount: float = Field(
        description="订单金额，单位为元"
    )

    status: str = Field(
        description="订单当前状态"
    )

    has_risk: bool = Field(
        description="订单是否存在明显风险"
    )

    summary: str = Field(
        description="订单分析总结"
    )


# ==================================
# 4. 创建 Pydantic 输出解析器
# ==================================

parser = PydanticOutputParser(
    pydantic_object=OrderAnalysis
)


# ==================================
# 5. 创建 Prompt
# ==================================

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        你是订单数据分析专家。

        请根据用户提供的订单信息进行分析。

        必须按照指定的数据格式输出，不要输出其他无关内容。

        {format_instructions}
        """
    ),
    (
        "human",
        "{question}"
    )
])


# ==================================
# 6. 构建执行链
# ==================================

chain = prompt | llm | parser


# ==================================
# 7. 执行测试
# ==================================

def main():

    question = """
    请分析以下订单：

    订单编号：A1001
    订单金额：199.00元
    订单状态：已发货
    用户ID：1

    请判断是否存在明显风险。
    """

    result = chain.invoke({
        "question": question,
        "format_instructions": parser.get_format_instructions()
    })

    print("\n========== 结构化输出 ==========")

    print(result)

    print("\n========== 单独读取字段 ==========")

    print("订单编号：", result.order_no)
    print("订单金额：", result.amount)
    print("订单状态：", result.status)
    print("是否存在风险：", result.has_risk)
    print("分析总结：", result.summary)

    print("\n========== 转换为字典 ==========")

    print(result.model_dump())


if __name__ == "__main__":
    main()
