
from pathlib import Path

from langchain.tools import tool


# 获取当前文件所在目录
BASE_DIR = Path(__file__).resolve().parent

# Skill 根目录
SKILLS_DIR = BASE_DIR / "skills"


@tool
def load_skill(skill_name: str) -> str:
    """
    根据 Skill 名称加载对应的 SKILL.md 文件。

    当用户需要执行特定领域任务，
    且需要获取对应的任务规范时，调用此工具。
    """

    # 防止路径穿越
    if not skill_name or Path(skill_name).name != skill_name:
        return "错误：Skill 名称不合法"

    # 拼接 Skill 文件路径
    skill_path = SKILLS_DIR / skill_name / "SKILL.md"

    # 检查文件是否存在
    if not skill_path.is_file():
        return f"错误：没有找到名为 {skill_name} 的 Skill"

    # 读取文件
    content = skill_path.read_text(encoding="utf-8")

    return content


if __name__ == "__main__":

    # 测试 Tool
    result = load_skill.invoke({
        "skill_name": "order-analysis"
    })

    print("=== Agent Skill Tool 加载结果 ===")
    print(result)
