# OnwordChat

一个基于 PostgreSQL + pgvector 的 RAG 问答项目：文档切分、向量化后写入 pgvector 向量库，用户提问时做相似度检索并交由大模型生成回答；聊天记录同步到 PostgreSQL 数据库。

目前上下文只有五条，且不会根据上下文在向量库检索。嵌入模型用的硅基流动的bge-m3。

知识库写入在ingest.py，只做了通过文件夹内的knowledge.json录入向量库。

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


