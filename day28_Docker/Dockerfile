
# 1. 使用 Python 3.10 官方轻量镜像
FROM python:3.10-slim

# 2. 设置容器内工作目录
WORKDIR /app

# 3. 安装系统依赖（用于部分 Python 包编译）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 4. 复制依赖清单
COPY day28_Docker/requirements.txt /app/requirements.txt

# 5. 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 6. 复制 Day26 数据库模块
COPY day26_MySQL /app/day26_MySQL

# 7. 复制 Day27 JWT 项目
COPY day27_JWT /app/day27_JWT

# 8. 设置 Python 模块搜索路径
ENV PYTHONPATH="/app/day27_JWT:/app/day26_MySQL"

# 9. 设置工作目录
WORKDIR /app/day27_JWT

# 10. 暴露服务端口
EXPOSE 8000

# 11. 启动 FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
