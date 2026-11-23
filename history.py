# 保存和读取聊天记录的接口
# 
import os

import psycopg
from dotenv import load_dotenv


load_dotenv()


# 保存问答到数据库
def save_turn(chat_id: str, question: str, answer: str) -> None:
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:

        # 第一次提问时创建会话，用问题的前 16 个字作标题。后续追问沿用原会话。
        conn.execute(
            "INSERT INTO conversations (id, title) VALUES (%s, %s) ON CONFLICT(id) DO NOTHING",
            (chat_id, question[:16]),
)

        # 创建 messages 表。
        insert_message = "INSERT INTO messages (conversation_id, role, content) VALUES (%s, %s, %s)"
        conn.execute(insert_message, (chat_id, "user", question))       # 写入提问
        conn.execute(insert_message, (chat_id, "assistant", answer))    # 写入回答
    pass


# 查询问答接口，只返回chat_id , title
def list_conversations():
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        rows=conn.execute("""
        SELECT id, title
        FROM conversations
        ORDER BY time DESC;
        """).fetchall()

        conversations = []
        for chat_id, title in rows:
            conversations.append({"id": chat_id, "title": title})

        return conversations
# 根据chat_id查询具体问题，返回role ,content
def list_messages(chat_id):
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
            rows=conn.execute("""
            SELECT  role, content
            FROM messages
            WHERE conversation_id = %s
            ORDER BY id ASC;
            """,(chat_id,)).fetchall()
    
            conversations = []
            for role, content in rows:
                conversations.append({"role": role, "content": content})
    
            return conversations



# 根据chat_id查询历史记录（但只返回最近五条，给对话的时候调用），返回role ,content
def list_recent_messages(chat_id):
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
            rows=conn.execute("""
            SELECT  role, content 
            FROM( 
                SELECT  id, role, content FROM messages
                WHERE conversation_id = %s
                ORDER BY id DESC
                LIMIT 5 )t
            ORDER BY id ASC;
            """,(chat_id,)).fetchall()
    
            conversations = []
            for role, content in rows:
                conversations.append({"role": role, "content": content})
    
            return conversations



if __name__ == "__main__":
    from uuid import uuid4

    chat_id = str(uuid4())
    save_turn(chat_id, "普通图书能借几天？", "普通图书可以借 21 天。")

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        rows = conn.execute(
            "SELECT role, content FROM messages WHERE conversation_id = %s ORDER BY id",
            (chat_id,),
        ).fetchall()
        print(rows)
