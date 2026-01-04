from fastapi import APIRouter
from db.mongo import chats_collection
from pydantic import BaseModel
from bson import ObjectId
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from fastapi import Request
from datetime import datetime, timezone
from ai.llm import get_ai_reply,stream_ai_reply


router=APIRouter()

class ChatRequest(BaseModel):
    message: str



@router.get("/")
def root():
    return {"message": "can you see me "}

@router.get('/chats')
def get_chats():
    chats=list(chats_collection.find().sort('created_at',1))
    for chat in chats:
        chat['_id']=str(chat['_id'])
    print('chat working')
    return chats



@router.post("/chat")
def chat(data: ChatRequest):
    user_message = data.message
    print('working')
    chats_collection.insert_one({
        'role':'user',
        'reply':user_message,
        'created_at':datetime.now(timezone.utc)
    })

    ai_reply = get_ai_reply(user_message)

    chats_collection.insert_one({
        'role':'assistant',
        'reply':ai_reply,
        'created_at':datetime.now(timezone.utc)
    })
    return {
        "role": "assistant",
        "reply":ai_reply,
        'created_at':datetime.now(timezone.utc)
    }

@router.post('/chat/stream')
def chat_stream(data:ChatRequest,request:Request):
    user_message=data.message
    
    chats_collection.insert_one({
        'role':'user',
        'reply':user_message,
        'created_at':datetime.now(timezone.utc)
    })
    return StreamingResponse(
        stream_ai_reply(user_message,request),
        media_type='text/plain'
    )




@router.delete('/chat/{chat_id}')
def chat_delete(chat_id:str):
    result=chats_collection.delete_one({
        "_id":ObjectId(chat_id)
    })
    if(result.deleted_count==0):
        raise HTTPException(
            status_code=404,
            detail='chat not found'
        )
    return {'message':'chat deleted'}

@router.delete('/chats')
def clear_coversation():
    result=chats_collection.delete_many({})
    return{
        'message':'all deleted',
        'deleted_count':result.deleted_count
    }





