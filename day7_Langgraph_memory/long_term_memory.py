import sqlite3

DB_PATH = "long_term_memory.db"
def get_connection():
    return sqlite3.connect(DB_PATH)
def init_db():
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute(  # 执行创建数据表的 SQL
        """
        CREATE TABLE IF NOT EXISTS user_memory (
            user_id TEXT NOT NULL,
            memory_key TEXT NOT NULL,
            memory_value TEXT NOT NULL,
            PRIMARY KEY (user_id, memory_key)
        )
        """
    )
    conn.commit()
    conn.close()
def save_memory(user_id,key,value):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO user_memory
        (user_id, memory_key, memory_value)
        VALUES (?, ?, ?)
        """,
        (user_id,key,value)
    )
    conn.commit()
    conn.close()
def get_memory(user_id):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute(  # 查询指定用户的长期记忆
        """
        SELECT memory_key, memory_value
        FROM user_memory
        WHERE user_id = ?
        """,
        (user_id,)
    )
    rows=cursor.fetchall()
    conn.close()
    return {key:value for key,value in rows}
init_db()