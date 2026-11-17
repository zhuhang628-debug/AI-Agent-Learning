# Day27 JWT 身份认证与权限控制

## 一、项目介绍
本项目基于 FastAPI、MySQL 和 PyJWT，实现用户注册、登录、JWT 身份认证及用户数据权限隔离，构建基础的后端用户认证系统。

## 二、技术栈
- FastAPI：后端接口开发
- SQLAlchemy：数据库 ORM
- MySQL：用户数据存储
- PyJWT：JWT Token 生成与解析
- pwdlib + Argon2：密码哈希及验证
- HTTPBearer：提取请求头中的 Bearer Token
- Depends：FastAPI 依赖注入

## 三、项目结构
```text
day27_JWT/
├── main.py
├── auth.py
├── security.py
├── schemas.py
├── test_security.py
└── README.md
```

数据库连接及 User ORM 模型复用 Day26_MySQL 项目。

## 四、核心功能

### 1. 密码安全
- 使用 Argon2 对用户密码进行哈希。
- 注册时保存密码哈希，不保存明文密码。
- 登录时通过 verify_password 验证密码。

### 2. JWT 身份认证
- 用户登录成功后生成 JWT Access Token。
- Token 使用 HS256 算法签名。
- Payload 保存用户 ID（sub）和过期时间（exp）。
- 使用 PyJWT 验证 Token 签名和有效期。

### 3. 用户注册与登录
- POST /auth/register：用户注册。
- POST /auth/login：用户登录。

### 4. 当前用户身份识别
- 使用 HTTPBearer 从请求头提取 Token。
- 使用 get_current_user 验证 Token。
- 根据 Token 中的用户 ID 查询 MySQL。
- 使用 Depends 将当前用户注入业务接口。

### 5. 用户数据权限隔离
- GET /auth/me：获取当前登录用户信息。
- GET /auth/users/{user_id}：查询指定用户信息。
- 通过比较请求用户 ID 与当前登录用户 ID，限制用户只能访问自己的数据。

## 五、接口测试

| 接口 | 测试结果 |
|---|---|
| POST /auth/register | 注册成功 |
| POST /auth/login | 登录成功，返回 JWT |
| GET /auth/me（无 Token） | 401 |
| GET /auth/me（有效 Token） | 200 |
| GET /auth/users/4（本人） | 200 |
| GET /auth/users/5（其他用户） | 403 |

## 六、关键知识点
1. 密码哈希与密码验证。
2. JWT 签名、Payload 和过期时间。
3. FastAPI HTTPBearer 身份认证。
4. Depends 依赖注入。
5. Authentication 与 Authorization 的区别。
6. 基于用户 ID 的数据权限隔离。
7. FastAPI 与 SQLAlchemy 的整合。

## 七、项目总结
本项目完成了基于 FastAPI 和 JWT 的用户认证模块，实现了用户注册、登录、Token 签发与验证，以及基于当前登录用户的数据权限控制，为后续 AI Agent 服务提供了基础的用户身份认证和业务数据隔离能力。