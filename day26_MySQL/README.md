# Day26 - FastAPI + MySQL 数据库工程化

## 一、项目介绍

本项目基于 FastAPI、SQLAlchemy 和 MySQL，实现一个分层架构的用户管理 API 服务。

通过本项目学习 Python 后端开发中的数据库连接管理、ORM 映射、数据校验、CRUD 操作和业务逻辑分层，为后续 AI Agent 项目和比赛问答系统提供数据库开发基础。

## 二、技术栈

- Python 3.10
- FastAPI：构建 HTTP API 服务
- SQLAlchemy 2.x：ORM 数据库操作
- PyMySQL：Python MySQL 驱动
- MySQL：关系型数据库
- Pydantic：请求参数校验和响应数据管理
- Uvicorn：运行 FastAPI 服务
- python-dotenv：读取环境变量
- Navicat：数据库可视化管理

## 三、项目结构

```text
day26_MySQL/
├── routers/
│   ├── __init__.py
│   └── users.py
├── database.py
├── models.py
├── schemas.py
├── crud.py
├── services.py
├── main.py
├── create_tables.py
├── test_db.py
└── README.md
```

数据库配置统一保存在项目根目录 `.env` 中，不在子项目重复存放。

## 四、核心功能

### 1. MySQL 数据库连接

使用 SQLAlchemy 创建数据库连接引擎，通过 PyMySQL 连接本地 MySQL。

主要配置：
- Engine：管理数据库连接。
- SessionLocal：创建数据库 Session。
- pool_size：配置连接池基础连接数量。
- max_overflow：配置连接池额外连接数量。
- pool_pre_ping：使用连接前检查连接有效性。
- get_db：通过 FastAPI 依赖注入提供数据库 Session，并在请求结束后关闭。

### 2. ORM 数据模型

通过 SQLAlchemy 2.x 定义 User 模型，将 Python 类映射为 MySQL 数据表。

users 表字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| id | Integer | 主键、自增 |
| username | String(50) | 用户名，唯一且非空 |
| email | String(100) | 邮箱，唯一且非空 |
| age | Integer | 年龄，非空 |

通过 Base.metadata.create_all() 创建数据表。

### 3. Pydantic Schema

使用 Pydantic 定义请求和响应数据结构：

- UserCreate：创建用户的数据校验。
- UserUpdate：修改用户的数据校验，支持部分字段更新。
- UserResponse：统一用户响应格式。
- ConfigDict(from_attributes=True)：支持从 SQLAlchemy ORM 对象读取属性。

### 4. CRUD 数据操作

在 crud.py 中封装数据库操作：

- create_user：创建用户。
- get_users：查询所有用户。
- get_user_by_id：根据 ID 查询用户。
- update_user：修改用户。
- delete_user：删除用户。

### 5. Service 业务逻辑层

在 services.py 中封装业务规则：

- register_user：注册用户，检查用户名和邮箱是否重复。
- list_users：查询用户列表。
- get_user：查询指定用户，不存在时抛出异常。
- modify_user：修改用户信息。
- remove_user：删除用户。

### 6. Router 接口层

在 routers/users.py 中定义用户管理接口，使用 Depends(get_db) 注入数据库 Session。

### 7. FastAPI 服务

main.py 注册用户管理 Router，并提供健康检查接口。

## 五、API 接口

服务启动后访问 `/docs` 查看 Swagger 接口文档。

| 请求方式 | 接口 | 功能 |
|---|---|---|
| GET | /health | 健康检查 |
| POST | /users/ | 创建用户 |
| GET | /users/ | 查询所有用户 |
| GET | /users/{user_id} | 查询指定用户 |
| PUT | /users/{user_id} | 修改用户 |
| DELETE | /users/{user_id} | 删除用户 |

## 六、环境配置

Python 依赖安装：

```bash
pip install fastapi uvicorn sqlalchemy pymysql python-dotenv
```

在项目根目录 `.env` 中配置：

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=你的MySQL密码
DB_NAME=agent_db
```

请使用自己的 MySQL 账号和密码，不要将 `.env` 上传到 GitHub。

创建数据库：

```sql
CREATE DATABASE agent_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

## 七、运行项目

在项目根目录执行：

```powershell
venv\Scripts\python.exe -m pip install fastapi uvicorn sqlalchemy pymysql python-dotenv
```

创建数据库表：

```powershell
venv\Scripts\python.exe day26_MySQL/create_tables.py
```

启动 FastAPI：

```powershell
venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000 --app-dir day26_MySQL
```

打开 Swagger：

http://127.0.0.1:8000/docs

## 八、测试结果

已完成以下功能测试：

- MySQL 数据库连接成功。
- SQLAlchemy Engine 和 Session 创建成功。
- users 数据表创建成功。
- 用户创建成功。
- 用户列表查询成功。
- 根据 ID 查询用户成功。
- 用户信息修改成功。
- 用户删除成功。
- 年龄填写 150，触发 HTTP 422 参数校验错误。
- 重复用户名注册，触发 HTTP 400 业务错误。

## 九、核心知识点总结

1. SQLAlchemy Engine：数据库引擎及连接池管理。
2. Session：数据库会话和事务操作。
3. DeclarativeBase：ORM 模型基类。
4. mapped_column：定义数据库字段。
5. Pydantic Schema：请求和响应数据校验。
6. CRUD：封装数据库增删改查。
7. Service：处理业务规则。
8. APIRouter：拆分和管理 API 路由。
9. Depends：FastAPI 依赖注入。
10. get_db：管理数据库 Session 生命周期。

## 十、学习收获

本项目完成了 FastAPI 与 MySQL 的整合，掌握了 SQLAlchemy 2.x ORM 的基本使用，以及数据库连接池、Session、Model、Schema、CRUD 和 Service 分层开发方式。

通过用户管理 API 的完整开发，理解了 Python 后端项目从 HTTP 请求、参数校验、业务逻辑处理到数据库持久化的执行流程。

项目采用与 Spring Boot 类似的分层思想，将接口层、业务层和数据库操作层解耦，为后续 AI Agent 应用开发和比赛问答系统的后端搭建提供了基础。