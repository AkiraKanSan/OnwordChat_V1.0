import os

import httpx
from dotenv import load_dotenv

load_dotenv()

base_url = os.environ["EMBEDDING_BASE_URL"].rstrip("/")
model = os.environ["EMBEDDING_MODEL"]
api_key = os.environ["EMBEDDING_API_KEY"]


def embed(text: str) -> list[float]:
    response = httpx.post(
        f"{base_url}/embeddings",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model":model,"input":text},       #  写请求体
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()          #  读取响应里的 JSON
    return data["data"][0]["embedding"]          #  取出第一条结果的向量


if __name__ == "__main__":
    vector = embed("一本书可以借多长时间？")
    print("向量维度", len(vector))
    print("前五个数", vector[:5])