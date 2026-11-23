#   创建嵌入客户端，供入库和检索共用
# 
import os

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

load_dotenv()


# 配置嵌入模型
base_url = os.environ["EMBEDDING_BASE_URL"].rstrip("/")
model = os.environ["EMBEDDING_MODEL"]
api_key = os.environ["EMBEDDING_API_KEY"]
# 创建嵌入客户端，供入库和检索共用  
embeddings = OpenAIEmbeddings(
    model=model,
    base_url=base_url,
    api_key=api_key,
    request_timeout=30,
    check_embedding_ctx_length=False,  # 直接把原文发给硅基流动
    model_kwargs={"encoding_format": "float"},
)





def embed(text: str) -> list[float]:
    return embeddings.embed_query(text)


if __name__ == "__main__":
    vector = embed("一本书可以借多长时间？")
    print("向量维度", len(vector))
    print("前五个数", vector[:5])