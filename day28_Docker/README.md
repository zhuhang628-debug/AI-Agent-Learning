# Day28 Docker 容器化部署

## 一、学习目标

本阶段主要学习如何使用 Docker 将 FastAPI 应用和 MySQL 数据库进行容器化部署，掌握多容器协同运行、容器网络通信、环境变量配置以及数据库数据持久化。

完成本阶段后，实现了 Day27 JWT 用户认证项目的 Docker 部署。

## 二、项目技术栈

- Python 3.10
- FastAPI
- Uvicorn
- SQLAlchemy
- MySQL 8.4
- Docker
- Docker Compose
- PyJWT
- Argon2

## 三、项目结构

```text
AI-Agent-Learning/
├── day26_MySQL/
│   ├── routers/
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── services.py
│   ├── main.py
│   └── create_tables.py
│
├── day27_JWT/
│   ├── main.py
│   ├── auth.py
│   ├── security.py
│   ├── schemas.py
│   └── test_security.py
│
├── day28_Docker/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── docker-compose.yml
│   └── README.md
│
├── .env
├── .dockerignore
└── venv/
```

## 四、Dockerfile 配置

Dockerfile 用于定义 FastAPI 应用镜像的构建过程。

主要步骤：

1. 使用 Python 3.10 slim 作为基础镜像。
2. 设置容器工作目录。
3. 安装 gcc 等构建依赖。
4. 复制 requirements.txt 并安装 Python 依赖。
5. 复制 Day26 数据库模块和 Day27 JWT 项目代码。
6. 配置 PYTHONPATH，解决跨目录模块导入问题。
7. 启动 Uvicorn 服务。

核心配置：

```dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY day28_Docker/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY day26_MySQL /app/day26_MySQL
COPY day27_JWT /app/day27_JWT

ENV PYTHONPATH="/app/day27_JWT:/app/day26_MySQL"

WORKDIR /app/day27_JWT

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

其中，`0.0.0.0` 表示 Uvicorn 监听容器内所有网络接口，使宿主机能够通过 Docker 端口映射访问 FastAPI 服务。

## 五、Docker Compose 配置

使用 Docker Compose 统一管理 FastAPI 和 MySQL 两个容器。

### 1. MySQL 服务

- 使用 MySQL 8.4 镜像。
- 容器名称：day28-mysql。
- 容器内部端口：3306。
- 宿主机映射端口：3307。
- 使用 mysql_data Volume 保存数据库数据。
- 配置 healthcheck 检查数据库健康状态。

### 2. FastAPI 服务

- 根据 Dockerfile 构建应用镜像。
- 容器名称：day28-fastapi。
- 宿主机端口 8000 映射到容器端口 8000。
- 通过 env_file 加载根目录 `.env`。
- 将 DB_HOST 设置为 mysql，DB_PORT 设置为 3306。
- 使用 depends_on 和 service_healthy，确保 MySQL 健康后再启动应用。

### 3. 容器网络

两个服务加入同一个 Docker bridge 网络 day28-network。

FastAPI 容器访问 MySQL 时，使用服务名称 mysql 作为主机名，而不是 127.0.0.1。

### 4. 数据持久化

使用命名 Volume：

```yaml
volumes:
  mysql_data:
```

MySQL 数据存储在 Docker Volume 中，不依赖 MySQL 容器本身的生命周期。

## 六、环境变量配置

项目根目录 `.env` 统一管理数据库和 JWT 配置。

主要变量：

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=自己的数据库密码
DB_NAME=agent_db

JWT_SECRET_KEY=自己的JWT密钥
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

注意：

1. `.env` 不应提交到 GitHub。
2. Docker Compose 运行时通过 `--env-file .env` 加载环境变量。
3. FastAPI 容器内部的数据库地址由 Compose 覆盖为 `mysql:3306`。
4. `.dockerignore` 排除 `.env`，避免将密钥复制进镜像。

## 七、启动和部署

在项目根目录执行。

### 1. 检查 Docker 环境

```powershell
docker --version
docker compose version
docker info
```

### 2. 检查 Compose 配置

```powershell
docker compose --env-file .env -f day28_Docker/docker-compose.yml config
```

### 3. 构建并启动容器

```powershell
docker compose --env-file .env -f day28_Docker/docker-compose.yml up -d --build
```

### 4. 查看容器状态

```powershell
docker ps
```

正常情况下，应该看到：

- day28-fastapi：Up
- day28-mysql：Up (healthy)

### 5. 创建数据库表

```powershell
docker compose --env-file .env -f day28_Docker/docker-compose.yml exec app python /app/day26_MySQL/create_tables.py
```

### 6. 查看服务日志

```powershell
docker logs --tail 100 day28-fastapi
```

持续查看日志：

```powershell
docker logs -f day28-fastapi
```

## 八、接口测试

浏览器访问：

```text
http://localhost:8000/docs
```

### 1. 健康检查

接口：

```text
GET /health
```

预期返回：

```json
{
  "status": "ok"
}
```

### 2. 用户注册

接口：

```text
POST /auth/register
```

测试数据：

```json
{
  "username": "docker001",
  "email": "docker001@example.com",
  "age": 22,
  "password": "Docker123456"
}
```

注册成功后，用户数据写入 Docker MySQL。

### 3. 用户登录

接口：

```text
POST /auth/login
```

测试数据：

```json
{
  "username": "docker001",
  "password": "Docker123456"
}
```

登录成功后返回 JWT Token。

### 4. JWT 身份认证

在 Swagger 页面点击 Authorize，填写登录返回的 Token。

访问：

```text
GET /auth/me
```

成功返回当前登录用户信息，验证 JWT 身份认证流程。

## 九、数据库连接验证

本项目存在两套独立的 MySQL 数据库：

| 数据库 | 主机地址 | 端口 |
|---|---|---|
| Windows 本机 MySQL | 127.0.0.1 | 3306 |
| Docker MySQL | 127.0.0.1 | 3307 |

通过 Navicat 新建 Docker MySQL 连接：

- 主机：127.0.0.1
- 端口：3307
- 用户名：root
- 密码：根目录 `.env` 中配置的 DB_PASSWORD

进入 agent_db 数据库，查询 users 表：

```sql
USE agent_db;

SELECT * FROM users;
```

能够查询到 docker001，说明 FastAPI 已经成功连接 Docker MySQL，用户注册数据已写入容器数据库。

## 十、数据持久化测试

### 1. 停止并删除容器

```powershell
docker compose --env-file .env -f day28_Docker/docker-compose.yml down
```

### 2. 重新启动容器

```powershell
docker compose --env-file .env -f day28_Docker/docker-compose.yml up -d
```

### 3. 验证数据

重新访问 Swagger，使用 docker001 账号登录。

登录成功，并且 Navicat 中仍然可以查询到该用户，说明 MySQL 数据在容器停止、删除和重新创建后仍然保留。

注意：不要使用 `docker compose down -v`，否则会删除命名 Volume 及其中的数据。

## 十一、问题记录与解决

### 1. Docker Compose 无法读取环境变量

问题：执行 Compose 命令时提示 DB_PASSWORD、DB_NAME 未设置。

原因：Compose 默认没有从项目根目录正确加载 `.env`。

解决：

```powershell
docker compose --env-file .env -f day28_Docker/docker-compose.yml up -d --build
```

### 2. Docker 容器无法访问 Windows 本机数据库

原因：容器中的 127.0.0.1 指向容器自身，而不是 Windows 主机。

解决：FastAPI 容器通过 Compose 网络使用 MySQL 服务名 mysql 连接数据库。

### 3. 容器内部可以访问接口，但宿主机访问异常

排查过程中发现：

- 容器内部访问 `127.0.0.1:8000/health` 返回 200。
- Windows 通过 `localhost:8000/health` 返回 200。
- Windows 通过 `127.0.0.1:8000/health` 出现超时。

因此本次部署使用：

```text
http://localhost:8000/docs
```

访问 Swagger 文档。

### 4. 本机 Navicat 找不到 Docker 注册的用户

原因：Docker MySQL 和 Windows 本机 MySQL 是两个独立数据库。

解决：Navicat 新建端口为 3307 的 Docker MySQL 连接。

## 十二、学习总结

本阶段完成了 FastAPI + MySQL + JWT 项目的 Docker 容器化部署。

通过 Dockerfile 掌握了应用镜像的构建过程，通过 Docker Compose 实现 FastAPI 和 MySQL 多容器统一管理，通过 Docker Network 实现容器间服务通信，并通过 Volume 实现数据库数据持久化。

最终完成了用户注册、登录、JWT 身份认证以及容器重启后的数据保留验证。

Day28 完成后，已经具备将一个包含 API 服务、数据库和身份认证的后端应用进行容器化部署的基础能力，为后续问答系统比赛项目的开发和部署打下基础。