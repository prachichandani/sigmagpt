from fastapi import APIRouter
from db.mongo import chats_collection, conversations_collection
from pydantic import BaseModel
from bson import ObjectId
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from fastapi import Request
from datetime import datetime, timezone
from ai.llm import get_ai_reply,stream_ai_reply, generate_conversation_title


router=APIRouter()

class ChatRequest(BaseModel):
    message: str
    conversation_id: str

class ConversationResponse(BaseModel):
    _id: str
    title: str
    created_at: datetime



@router.get("/")
def root():
    return {"message": "can you see me "}

@router.get('/chats')
def get_chats(conversation_id: str):
    query = {"conversation_id": ObjectId(conversation_id)}

    chats = list(chats_collection.find(query).sort("created_at", 1))

    for chat in chats:
        chat["_id"] = str(chat["_id"])
        chat["conversation_id"] = str(chat["conversation_id"])

    print("chat working")
    return chats



@router.post("/chat")
def chat(data: ChatRequest):
    user_message = data.message
    conversation_id = data.conversation_id
    print('working')
    
    # Check if this is the first message and update title if needed
    conversation = conversations_collection.find_one({"_id": ObjectId(conversation_id)})
    if conversation and conversation.get('title') == 'New Conversation':
        new_title = generate_conversation_title(user_message)
        conversations_collection.update_one(
            {"_id": ObjectId(conversation_id)},
            {"$set": {"title": new_title}}
        )
    
    chats_collection.insert_one({
        'role':'user',
        'reply':user_message,
        'conversation_id': ObjectId(conversation_id),
        'created_at':datetime.now(timezone.utc)
    })

    ai_reply = get_ai_reply(user_message, ObjectId(conversation_id))

    chats_collection.insert_one({
        'role':'assistant',
        'reply':ai_reply,
        'conversation_id': ObjectId(conversation_id),
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
    conversation_id=data.conversation_id
    
    # Check if this is the first message and update title if needed
    conversation = conversations_collection.find_one({"_id": ObjectId(conversation_id)})
    if conversation and conversation.get('title') == 'New Conversation':
        new_title = generate_conversation_title(user_message)
        conversations_collection.update_one(
            {"_id": ObjectId(conversation_id)},
            {"$set": {"title": new_title}}
        )
    
    chats_collection.insert_one({
        'role':'user',
        'reply':user_message,
        'conversation_id': ObjectId(conversation_id),
        'created_at':datetime.now(timezone.utc)
    })
    return StreamingResponse(
        stream_ai_reply(user_message,request,ObjectId(conversation_id)),
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

@router.post('/conversations')
def create_conversation(first_message: str = None):
    title = "New Conversation"
    if first_message:
        title = generate_conversation_title(first_message)
    
    conversation = {
        'title': title,
        'created_at': datetime.now(timezone.utc)
    }
    result = conversations_collection.insert_one(conversation)
    conversation['_id'] = str(result.inserted_id)
    return conversation

@router.get('/conversations')
def get_conversations():
    conversations = list(conversations_collection.find().sort('created_at', -1))
    for conv in conversations:
        conv['_id'] = str(conv['_id'])
    return conversations

@router.delete('/conversations/{conversation_id}')
def delete_conversation(conversation_id: str):
    # Delete the conversation
    conv_result = conversations_collection.delete_one({
        "_id": ObjectId(conversation_id)
    })
    
    if conv_result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail='Conversation not found'
        )
    
    # Delete all messages in this conversation
    chats_result = chats_collection.delete_many({
        "conversation_id": ObjectId(conversation_id)
    })
    
    return {
        'message': 'Conversation deleted',
        'messages_deleted': chats_result.deleted_count
    }





