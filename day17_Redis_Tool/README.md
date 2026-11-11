# Day17 Redis Tool：Redis 缓存与 Agent 集成

## 一、学习目标

- 使用 Python Redis 客户端连接 Redis。
- 掌握 Redis Key、JSON 序列化和 TTL 过期机制。
- 将 Redis 缓存集成到 LangChain Agent Tool。
- 实现 Redis + MySQL 的 Cache Aside 缓存模式。

## 二、核心知识点

| 知识点 | 作用 |
|---|---|
| Redis Client | 使用 `redis.Redis()` 连接 Redis |
| Cache Key | 使用 `order:{order_no}` 区分订单缓存 |
| JSON 序列化 | `json.dumps()` 写入，`json.loads()` 读取 |
| TTL | 设置缓存有效期，避免缓存永久存在 |
| Cache HIT | Redis 中存在数据，直接返回 |
| Cache MISS | Redis 中没有数据，查询 MySQL 并回填缓存 |
| Cache Aside | 先查缓存，未命中再查数据库 |

## 三、核心代码

### 1. Redis 连接

```python
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True
)
```

### 2. 缓存读取与回填

```python
cache_key = f"order:{order_no}"
cached_data = redis_client.get(cache_key)

if cached_data:
    order = json.loads(cached_data)
    return order

order = query_mysql(order_no)

redis_client.set(
    cache_key,
    json.dumps(order, ensure_ascii=False),
    ex=300
)
```

### 3. Agent 集成

使用 `@tool` 将订单查询逻辑封装为 `query_order` 工具，通过 LangChain 1.x 的 `create_agent()` 接入 Agent。

## 四、执行流程

1. 用户提出订单查询需求。
2. Agent 调用 `query_order` 工具。
3. 首先查询 Redis 缓存。
4. Cache HIT：直接返回缓存数据。
5. Cache MISS：查询 MySQL，将结果写入 Redis。
6. 设置 300 秒 TTL，返回订单信息。

## 五、测试结果

| 测试项目 | 测试结果 |
|---|---|
| Redis 连接 | 成功 |
| 首次查询 A1001 | Cache MISS |
| MySQL 查询 | 成功 |
| Redis 缓存写入 | 成功，TTL = 300s |
| 再次查询 A1001 | Cache HIT |
| Agent Tool Calling | 成功 |

## 六、学习总结

本次实现了 Redis 与 MySQL 的缓存集成，掌握了 Cache Aside 模式及缓存过期机制。通过将缓存逻辑封装为 LangChain Tool，使 Agent 能够优先读取 Redis，降低重复查询数据库的开销。同时了解了缓存与数据库数据不一致的问题，以及通过删除缓存实现缓存更新的基本思路。