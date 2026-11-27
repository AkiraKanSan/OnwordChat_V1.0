# 保存和读取聊天记录的接口
# 
import os
import psycopg
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()


# 保存问答到数据库,返回对话id
def save_turn(chat_id: str,user_id, question: str, answer: str) -> None:
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        if chat_id is None:
            # 第一次提问时创建会话，用问题的前 16 个字作标题。后续追问沿用原会话。
            row=conn.execute(
                """INSERT INTO conversations (user_id, title) 
                VALUES (%s, %s) 
                RETURNING id""",
                (user_id, question[:16]),
    ).fetchone()
            chat_id=row[0]
        else:
            # 追问写入已有会话，写入前再核对一次归属
            check_chat_owner(conn,chat_id,user_id)

        # 插入问答。
        insert_message = "INSERT INTO messages (conversation_id, role, content) VALUES (%s, %s, %s)"
        conn.execute(insert_message, (chat_id, "user", question))       # 写入提问
        conn.execute(insert_message, (chat_id, "assistant", answer))    # 写入回答
    return chat_id


# 查询问答接口，只返回chat_id , title
def list_conversations(user_id: int):
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        rows=conn.execute("""
        SELECT id, title
        FROM conversations
        WHERE user_id = %s
        ORDER BY time DESC
        """,(user_id,)).fetchall()

        conversations = []
        for chat_id, title in rows:
            conversations.append({"id": chat_id, "title": title})

        return conversations
# 根据chat_id查询具体问题，返回role ,content
def list_messages(chat_id, user_id: int):
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
            # 确认会话属于当前用户
            check_chat_owner(conn,chat_id,user_id)

                 
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

# 确认这段会话属于当前用户
def check_chat_owner(conn, chat_id, user_id: int):
    row = conn.execute(
        """SELECT id 
        FROM conversations 
        WHERE id = %s AND user_id = %s""",
        (chat_id, user_id),
    ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="会话不存在")

# 根据chat_id查询历史记录（但只返回最近五条，给对话的时候调用），返回role ,content
def list_recent_messages(chat_id,user_id:int):
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
            check_chat_owner(conn,chat_id,user_id)
            rows=conn.execute("""
            SELECT  role, content 
            FROM( 
                SELECT  id, role, content FROM messages
                WHERE conversation_id = %s
                ORDER BY id DESC
                LIMIT 10 )t
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
