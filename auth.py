# 登陆接口
# 
import os

import psycopg
from pydantic import BaseModel, Field
from pwdlib import PasswordHash
from fastapi import APIRouter, Depends, HTTPException, Request, Response


# 账号相关接口统一使用 /api/auth 前缀
router = APIRouter(prefix="/api/auth", tags=["账号"])
# 注册时生成密码哈希，登录时用同一个工具验证密码
password_hasher = PasswordHash.recommended()

# 注册接口接收的请求体，字段长度由 Pydantic 校验
class RegisterRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=8, max_length=128)

# 注册账号，成功后返回用户 ID 和用户名
@router.post("/register", status_code=201)
def register(body: RegisterRequest):
    username = body.username.strip()        # 去掉用户名首尾空格
    if not username:
        raise HTTPException(status_code=422, detail="用户名不能为空")

    password_hash = password_hasher.hash(body.password)     # 数据库只保存密码哈希

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        # 插入用户并取回 id 和用户名。用户名重复时跳过插入，fetchone() 返回 None
        row = conn.execute(
            """
            INSERT INTO users (username, password_hash)
            VALUES (%s, %s)
            ON CONFLICT (username) DO NOTHING
            RETURNING id, username
            """,
            (username, password_hash),
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=409, detail="用户名已存在")

    return {"id": row[0], "username": row[1]}



# 登录账号，验证成功后记住当前用户
@router.post("/login")
def login(body: RegisterRequest, request: Request):
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        row = conn.execute(
            "SELECT id, password_hash FROM users WHERE username = %s",
            (body.username.strip(),),
        ).fetchone()

    # 用户名不存在和密码错误时，给前端相同的提示
    if row is None:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    user_id, stored_hash = row
    if not password_hasher.verify(body.password, stored_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 登录状态里只存用户 ID，后面用它查询这个用户的聊天记录
    request.session["user_id"] = user_id
    return {"id": user_id}

# 从登录状态里取出用户 ID，聊天和历史记录接口也可以复用
def get_current_user_id(request: Request) -> int:
    user_id = request.session.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="请先登录")
    return user_id


# 查看当前登录的用户
@router.get("/me")
def get_me(user_id: int = Depends(get_current_user_id)):
    return {"id": user_id}


# 退出登录，清除当前浏览器的登录状态
@router.post("/logout", status_code=204)
def logout(request: Request):
    request.session.clear()
    return Response(status_code=204)