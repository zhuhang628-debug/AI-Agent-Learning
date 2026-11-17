
from security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token
)


# 1. 测试密码哈希
password = "123456"

hashed_password = get_password_hash(password)

print("原始密码:", password)
print("哈希密码:", hashed_password)


# 2. 测试密码验证
print("\n正确密码验证:", verify_password(
    "123456", hashed_password
))

print("错误密码验证:", verify_password(
    "654321", hashed_password
))


# 3. 测试 JWT 生成
token = create_access_token({
    "sub": "1"
})

print("\n生成的 JWT:")
print(token)


# 4. 测试 JWT 解析
payload = decode_access_token(token)

print("\n解析 JWT:")
print(payload)
