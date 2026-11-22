import os

import psycopg
from dotenv import load_dotenv

from embedding import embed

load_dotenv()



def search(question:str) -> list[tuple[str, str, float]]:
    query_vector = embed(question)    

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:               #连接数据库
        rows = conn.execute(
            """
            SELECT question, answer, embedding <=> %s::vector AS distance
            FROM knowledge
            ORDER BY distance ASC
            LIMIT 3
            """,
            (query_vector,),
        ).fetchall()
        return rows


if __name__ == "__main__":
    for row in search("能留多久？"):
        print(row)
