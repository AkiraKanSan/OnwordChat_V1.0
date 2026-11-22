from fastapi import FastAPI
from pydantic import BaseModel

from chat import ask

from pathlib import Path
from fastapi.responses import FileResponse


from history import save_turn , list_conversations ,list_messages

app = FastAPI()


class ChatRequest(BaseModel):
    question: str
    chatId: str | None = None

# 主页面
@app.get("/")
def home():
    return FileResponse(Path(__file__).with_name("index.html"))


# 查询问答的接口
@app.get("/api/conversations")
def get_conversations():
    return list_conversations()

# 读取历史记录
@app.get("/api/conversations/{chat_id}/messages")
def get_messages(chat_id: str):
    return list_messages(chat_id)


@app.post("/api/chat")
def chat(body: ChatRequest):

    if body.chatId is not None:
        historys=list_messages(body.chatId)
    else: historys=[]

    answer = ask(body.question,historys)       # 从请求体里取出问题和历史记录向大模型提问
    if body.chatId:
        save_turn(body.chatId, body.question, answer)

    return {"answer": answer}  # 把回答放进返回给调用方的 JSON

