from openai import OpenAI
from db.mongo import chats_collection
from fastapi import Request
from core.config import OPENAI_API_KEY,MEMORY_LIMIT
from datetime import datetime,timezone

client = OpenAI(api_key=OPENAI_API_KEY)

def get_recent_messages(limit: int):
    chats=( chats_collection.find({},{'_id':0})
           .sort('created_at',-1)
           .limit(limit)
           )
    messages=[]
    for chat in reversed(list(chats)):
        messages.append({
            'role':chat['role'],
            'content':chat['reply']
        })
    return messages



def get_ai_reply(user_message:str)->str:
    history=get_recent_messages(MEMORY_LIMIT)
    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
            {'role':'system','content':'You are a helpful assistant'},*history,
            {'role':'user','content':user_message}
        ]
    )
    return response.choices[0].message.content

async def stream_ai_reply(user_message: str,request:Request):
    history=get_recent_messages(MEMORY_LIMIT)
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},*history,
            {"role": "user", "content": user_message}
        ],
        stream=True
    )

    full_reply = ""

    try:
        for chunk in stream:
            if await request.is_disconnected():
                print('stop')
                break

            if chunk.choices[0].delta.content:
              token = chunk.choices[0].delta.content
              full_reply += token
              yield token
    
    finally:
        if full_reply.strip():
            chats_collection.insert_one({
            "role": "assistant",
            "reply": full_reply,
            'created_at':datetime.now(timezone.utc)
        })

    


