# OnwordChat

这是一个用 FastAPI、LangChain 和 PostgreSQL + pgvector 实现的图书馆 FAQ 问答服务。

目前上下文只有五条，利用langchain的接口加入了上下文在向量库检索。嵌入模型用的硅基流动的bge-m3。

知识库写入在ingest.py，暂时只做了通过文件夹内的knowledge.json录入向量库。

## 本地运行

下面的命令适用于 Windows PowerShell。开发环境使用 Python 3.12。先准备一个已启用 pgvector 的 PostgreSQL 数据库，并让应用账号拥有建表和读写权限。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

在 `.env` 中填入数据库连接、模型服务地址、模型名和密钥。当前表结构需要 1024 维 embedding。如果数据库通过 SSH 隧道访问，连接串使用本地转发端口。

```powershell
.\.venv\Scripts\python.exe db.py
.\.venv\Scripts\python.exe ingest.py
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

打开[聊天首页](http://127.0.0.1:8000/)或[接口文档](http://127.0.0.1:8000/docs)。


新增了一个POST /api/search ，可以单独查看检索到的问题、答案和distance。
空白问题也会被检索，但是空白输入被前端拦截了，不做处理了。