import os

import psycopg
from dotenv import load_dotenv

load_dotenv()

with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
    row = conn.execute("SELECT current_database() , current_user").fetchone()       #连接数据库输出第一行
    print(row)
    # 知识库
    conn.execute("""
    CREATE TABLE IF NOT EXISTS knowledge (
        id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        embedding vector(1024) NOT NULL
    )
""")
    # id和标题库
    conn.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
        title TEXT NOT NULL,
        time timestamptz NOT NULL DEFAULT now()
    )

    """
    )
    # 内容库
    conn.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id bigserial PRIMARY KEY,
        conversation_id uuid NOT NULL
                  REFERENCES conversations(id) ON DELETE CASCADE,
        role TEXT NOT NULL,
        content TEXT NOT NULL
    )

    """
    )

    # 再建一个user_id
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username text NOT NULL UNIQUE,
    password_hash text NOT NULL
    );

    ALTER TABLE conversations
    ADD COLUMN IF NOT EXISTS user_id integer REFERENCES users(id);  
        """
    )

    print(conn.execute("""
    SELECT to_regclass('public.conversations'), to_regclass('public.messages')
""").fetchone())


