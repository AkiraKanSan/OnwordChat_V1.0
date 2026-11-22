# 录入知识库接口
# 
import json
import os

import psycopg
from dotenv import load_dotenv

from embedding import embed
from pathlib import Path

load_dotenv()


Path=Path(__file__).with_name("knowledge.json")

with Path.open(encoding='utf-8') as file:
    data=json.load(file)
"""

格式：
{
  "items": [
    {"question": "普通图书可以借多久？", "answer": "普通图书一次可借 21 天。"},
    {"question": "借出的书可以续借吗？", "answer": "普通图书可续借一次，续借期为 14 天。"}
  ]
}
"""


with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
    for item in data["items"]:
        question =item["question"]
        answer = item["answer"]
        

        row = conn.execute(                                 # 对 question 去重
            """
            SELECT answer FROM knowledge WHERE question = %s
            """,
            (question,),  
        ).fetchone()
        print(row)

        # 新增知识库内容
        if row is None:
            
            print ("待新增",question)
            vector = embed(question)  #这一行要生成向量
            conn.execute(
            """
            INSERT INTO knowledge (question, answer, embedding)
            VALUES (%s, %s, %s::vector)
            """,
            (question, answer, vector), 
            )

            print ("已新增",question)

        elif row[0]!=answer:            # answer 不一致要更新
            print ("待更新",question)
            conn.execute("""
            UPDATE knowledge SET answer = %s WHERE question = %s

            """,(answer,question),)
            print ("已更新",question)
        else :
            print ("已存在",question)


'''
        row = conn.execute(
            """
            INSERT INTO knowledge (question, answer, embedding)
            VALUES (%s, %s, %s::vector)
            RETURNING id, question, vector_dims(embedding)
            """,
            (question, answer, vector),  #把向量列表转换成文本
        ).fetchone()
        print(row)'''