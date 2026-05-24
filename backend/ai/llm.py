import google.generativeai as genai
from db.mongo import chats_collection
from fastapi import Request
from core.config import GEMINI_API_KEY, MEMORY_LIMIT
from datetime import datetime, timezone

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

def generate_conversation_title(first_message: str) -> str:
    """Generate a short, descriptive title for a conversation based on the first message."""
    
    if not first_message or not first_message.strip():
        return "New Conversation"

    prompt = (
        "Generate a very short 3-5 word title for a conversation that starts with:\n"
        f"{first_message}\n\n"
        "Return only the title. No quotes, no extra text."
    )

    try:
        response = model.generate_content(prompt)
        
        title = response.text.strip().strip('"\'') if response.text else ""
        
        if not title:
            return "New Conversation"
        
        # Optional: limit title length
        words = title.split()
        if len(words) > 6:
            title = " ".join(words[:6])
        
        return title

    except Exception as e:
        print(f"Error generating title: {e}")
        return "New Conversation"


        
def get_recent_messages(limit: int, conversation_id: str):
    query = {'conversation_id': conversation_id}
    
    chats=( chats_collection.find(query,{'_id':0})
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



def get_ai_reply(user_message: str, conversation_id: str) -> str:
    history = get_recent_messages(MEMORY_LIMIT, conversation_id)
    
    # Format conversation for Gemini
    conversation = []
    for msg in history:
        conversation.append(f"{msg['role']}: {msg['content']}")
    conversation.append(f"user: {user_message}")
    
    full_prompt = "\n".join(conversation)
    
    response = model.generate_content(full_prompt)
    return response.text
    

async def stream_ai_reply(user_message: str, request: Request, conversation_id: str):
    history = get_recent_messages(MEMORY_LIMIT, conversation_id)
    
    # Format conversation for Gemini
    conversation = []
    for msg in history:
        conversation.append(f"{msg['role']}: {msg['content']}")
    conversation.append(f"user: {user_message}")
    
    full_prompt = "\n".join(conversation)
    
    full_reply = ""
    
    try:
        # Generate streaming response
        response = model.generate_content(full_prompt, stream=True)
        
        for chunk in response:
            if await request.is_disconnected():
                print('Client disconnected, stopping stream')
                break
                
            if chunk.text:
                token = chunk.text
                full_reply += token
                yield token
        
        yield "\n"
        
        # Save to database
        if full_reply.strip():
            try:
                chats_collection.insert_one({
                    "role": "assistant",
                    "reply": full_reply,
                    'conversation_id': conversation_id,
                    'created_at': datetime.now(timezone.utc)
                })
            except Exception as db_error:
                print(f"Database error: {db_error}")
                
    except Exception as e:
        print(f"Stream error: {e}")
        yield f"Error: {str(e)}\n"

    


