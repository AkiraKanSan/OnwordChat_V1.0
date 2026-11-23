import os

import httpx
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from search import search

load_dotenv()


# 系统提示词

system_content="""你是明川市图书馆的读者服务助手。请根据本次请求提供的 FAQ，用简洁、自然的中文回答读者的问题。

【如何使用 FAQ】
每条 FAQ 包含 question 和 answer。question 用来确定这条规则适用于什么对象、什么情形，answer 是回答的依据。检索结果只是候选资料，排在第一条不代表它一定能回答读者的问题。

先判断读者问的是什么，再选择适用的 FAQ。读者不必使用和标准问题一样的措辞。同义表达可以匹配，但对象、办理事项和适用条件必须一致。例如，预约图书的取书期限和讨论室的签到期限是两项不同的规则。

【如何回答】
- 资料足以回答时，直接给出结论，保留必要的时间、数量、地点和办理条件。可以合并互相补充的 FAQ。
- 资料只回答了问题的一部分时，先回答有依据的部分，再具体指出哪一部分缺少规定。
- 资料不足时，明确说明“现有资料没有说明……”并点明读者所问的事项。不要用相近规则代替答案，也不要根据常识、其他图书馆的做法或资料中的沉默推断结论。一般规则不能自动证明它在某个特殊情形下仍然适用。
- 读者的说法有歧义，且不同理解会得到不同答案时，先问一个简短的澄清问题。例如，读者只问“预约保留多久”，可以问“您指的是预约图书到馆后的取书期限，还是讨论室预约开始后的签到期限？”
- 如果适用于同一情形的资料相互冲突，简要指出冲突之处，说明现有资料无法确定答案。

【表达方式】
通常用一到两句话作答。读者问“几天”就先说天数，问“怎么办”就先说办理步骤。无需复述标准问题、罗列无关规定或解释检索过程。不要声称已查询读者账户、完成预约或办理其他业务。"""

# 向大模型提问提问
def ask(question: str,history=None) -> str:
    # langchain 创建 model
    model = ChatOpenAI(
        model = os.getenv("CHAT_MODEL"),
        base_url = os.getenv("CHAT_BASE_URL"),
        api_key = os.getenv("CHAT_API_KEY"),
        timeout = 30,

    )
    # 根据聊天记录补全检索问题
    query = build_search_query(question, history, model)
    rows = search(query)            #向量库查询    
    print("检索问题：", query)             
    context = "\n\n".join(
        f"资料 {i}\n问：{stored_question}\n答：{answer}"
        for i, (stored_question, answer, distance) in enumerate(rows, start=1)
    )
    if history is None:
        history=[]
    messages=[
                {"role": "system", "content": system_content}
            ]
    for message in history:
        messages.append(message)
    messages.append({"role": "user", "content": f"[用户问题]:{question}\n"f"[参考资料]:{context}"})


    # 发送消息
    reply = model.invoke(messages)

    # 返回文本
    return reply.content

# 根据历史消息，通过大模型输出要检索的问题
def build_search_query(question, history, model):
    # 首轮没有聊天记录，直接用原问题检索
    if not history:
        return question

    # 取最近五条聊天记录，最后放上读者这次的原话
    prompt = ChatPromptTemplate.from_messages([
    ("system", "根据对话，把读者最后一句话补成一个可以单独检索的问题。保留原意，只输出问题。"),                  #  固定的系统提示词
    MessagesPlaceholder("history"),        # 历史消息插槽
    ("human", "{question}"),               # 本次问题占位符
])
    # 流程
    chain = prompt | model | StrOutputParser()


    # 让模型补全检索问题，返回改写后的文本
    reply = chain.invoke({"history":history,"question":question})
    return reply

if __name__ == "__main__":
    print(ask(input("你的问题：")))