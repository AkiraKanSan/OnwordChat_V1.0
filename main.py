from fastapi import FastAPI
from pydantic import BaseModel
from chat import ask
from pathlib import Path
from fastapi.responses import FileResponse
from search import search
from history import save_turn , list_conversations ,list_messages ,list_recent_messages
from auth import router as auth_router
import os
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware
from fastapi import Depends, FastAPI
from auth import get_current_user_id, router as auth_router
from uuid import UUID

load_dotenv()

app = FastAPI()

# 给登录 Cookie 加签名，后续请求可以从 session 取出用户 ID
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ["SESSION_SECRET"],
    same_site="lax",
    https_only=False,  # 本地用 HTTP 调试，部署到 HTTPS 域名后改为 True
)


app.include_router(auth_router)     # 接入账号接口，启动 main:app 时一起生效


class ChatRequest(BaseModel):
    question: str
    chatId: UUID | None = None

# 主页面
@app.get("/")
def home():
    return FileResponse(Path(__file__).with_name("index.html"))


# 查询问答的接口，根据账号查询
@app.get("/api/conversations")
def get_conversations(user_id: int = Depends(get_current_user_id)):
    return list_conversations(user_id)

# 读取历史记录
@app.get("/api/conversations/{chat_id}/messages")
def get_messages(chat_id: UUID, user_id: int = Depends(get_current_user_id)):
    return list_messages(chat_id, user_id)

# 对话接口
@app.post("/api/chat")
def chat(body: ChatRequest,user_id:int = Depends(get_current_user_id)):
    # 加入上下文
    historys=[]
    if body.chatId is not None:             
        historys=list_recent_messages(body.chatId,user_id)
    

    answer = ask(body.question,historys)       # 从请求体里取出问题和历史记录向大模型提问
    chat_id = save_turn(body.chatId, user_id, body.question, answer)
    return {"chatId": chat_id, "answer": answer}






# 下面是调试用的，查询知识库检索的内容，返回question, answer, distance
class SearchRequest(BaseModel):
    question : str
    
@app.post("/api/search")
def search_knowledge(body:SearchRequest):
    rows = search(body.question)    # 从知识库检索到内容，会输出三条
    results =[]
    for row in rows:
        results.append({
            "question" : row[0],
            "answer" : row[1],
            "distance" : row[2],

        })

    return results                  # 整理数据返回