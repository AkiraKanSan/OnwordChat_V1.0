from fastapi import FastAPI
from pydantic import BaseModel

from chat import ask

from pathlib import Path
from fastapi.responses import FileResponse

from search import search


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

# 对话接口
@app.post("/api/chat")
def chat(body: ChatRequest):
    # 加入上下文
    if body.chatId is not None:             
        historys=list_messages(body.chatId)
    else: historys=[]

    answer = ask(body.question,historys)       # 从请求体里取出问题和历史记录向大模型提问
    if body.chatId:
        save_turn(body.chatId, body.question, answer)

    return {"answer": answer}  # 把回答放进返回给调用方的 JSON

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