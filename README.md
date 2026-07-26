# AI Agent 学习项目

30 天冲刺 AI Agent 实习，从 FastAPI 基础到企业级 RAG 系统。

## 技术栈

- Python / FastAPI
- LangChain / LangGraph
- DeepSeek API
- Git

## 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/zhuhang628-debug/AI-Agent-Learning.git

# 2. 进入项目
cd AI-Agent-Learning

# 3. 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 4. 安装依赖
pip install fastapi uvicorn openai python-dotenv

# 5. 配置 API Key
# 创建 .env 文件，写入：DEEPSEEK_API_KEY=你的密钥

# 6. 启动服务
uvicorn main:app --reload