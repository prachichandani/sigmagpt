import google.generativeai as genai
from db.mongo import chats_collection
from fastapi import Request
from core.config import GEMINI_API_KEY, MEMORY_LIMIT
from datetime import datetime, timezone
from typing import List, Dict, Optional
from ai.rag import hybrid_search
from ai.reranker import rerank_chunks

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


def rewrite_query(user_query: str, conversation_id: str) -> str:
    """
    Rewrite follow-up questions into standalone retrieval queries using chat history.
    """
    if not user_query or not user_query.strip():
        return user_query

    history = get_recent_messages(MEMORY_LIMIT, conversation_id)

    if not history:
        return user_query

    conversation_context = []

    for msg in history[-MEMORY_LIMIT:]:
        role = msg.get("role", "user")
        content = msg.get("content", "")

        if content:
            conversation_context.append(f"{role}: {content[:1000]}")

    if not conversation_context:
        return user_query

    context_str = "\n".join(conversation_context)

    prompt = f"""
You are a query rewriting module for a RAG system.

Your task:
- Rewrite the current user question into a standalone retrieval query.
- Use conversation history only if needed.
- If the current question is already clear and standalone, return it unchanged.
- Do not answer the question.
- Do not add explanations.
- Return only the rewritten query.

Conversation history:
{context_str}

Current user question:
{user_query}

Standalone retrieval query:
""".strip()

    try:
        response = model.generate_content(prompt)

        rewritten_query = getattr(response, "text", "").strip()

        if not rewritten_query:
            return user_query

        if len(rewritten_query) < 3:
            return user_query

        if len(rewritten_query) > 500:
            return user_query

        return rewritten_query

    except Exception as e:
        print(f"Query rewriting error: {e}")
        return user_query

def get_ai_reply(
    user_message: str,
    conversation_id: str,
    use_rag: bool = False
) -> Dict:
    """
    Get AI reply with optional RAG context injection.
    
    Args:
        user_message: User's message
        conversation_id: Conversation ID
        use_rag: Whether to use RAG for context retrieval
    
    Returns:
        Dict with 'reply' and optional 'sources'
    """
    history = get_recent_messages(MEMORY_LIMIT, conversation_id)
    
    if use_rag:
        # Rewrite query for better retrieval
        rewritten_query = rewrite_query(user_message, conversation_id)
        
        # Retrieve and rerank chunks
        retrieved_chunks = hybrid_search(rewritten_query, conversation_id)
        reranked_chunks = rerank_chunks(rewritten_query, retrieved_chunks)
        
        # Build context from chunks
        context_parts = []
        sources = []
        
        for idx, chunk in enumerate(reranked_chunks):
            context_parts.append(f"[Source {idx + 1}]: {chunk['text']}")
            sources.append({
                "filename": chunk["metadata"].get("filename", "Unknown"),
                "page_number": chunk["metadata"].get("page_number"),
                "chunk_index": chunk["metadata"].get("chunk_index"),
                "score": chunk.get("rerank_score", chunk.get("score", 0))
            })
        
        context_str = "\n\n".join(context_parts)
        
        # Build RAG prompt
        prompt = (
            "You are a helpful assistant that answers questions based on the provided context from uploaded documents.\n\n"
            f"Context from documents:\n{context_str}\n\n"
            f"Question: {user_message}\n\n"
            "Instructions:\n"
            "- Answer ONLY using the provided context\n"
            "- If the answer is not in the context, say 'I couldn't find this information in the uploaded documents'\n"
            "- Include source citations in your answer using [Source X] format\n"
            "- Be concise and accurate\n"
        )
    else:
        # Normal chat without RAG
        conversation = []
        for msg in history:
            conversation.append(f"{msg['role']}: {msg['content']}")
        conversation.append(f"user: {user_message}")
        
        prompt = "\n".join(conversation)
        sources = []
    
    try:
        response = model.generate_content(prompt)
        reply = response.text if response.text else "I apologize, but I couldn't generate a response."
        
        result = {"reply": reply}
        
        if use_rag and sources:
            result["sources"] = sources
        
        return result
    
    except Exception as e:
        print(f"Error generating reply: {e}")
        return {"reply": f"Error: {str(e)}", "sources": [] if use_rag else None}
    

async def stream_ai_reply(
    user_message: str,
    request: Request,
    conversation_id: str,
    use_rag: bool = False
):
    """
    Stream AI reply with optional RAG context injection.
    
    Args:
        user_message: User's message
        request: FastAPI Request object
        conversation_id: Conversation ID
        use_rag: Whether to use RAG for context retrieval
    """
    history = get_recent_messages(MEMORY_LIMIT, conversation_id)
    sources = []
    
    if use_rag:
        # Rewrite query for better retrieval
        rewritten_query = rewrite_query(user_message, conversation_id)
        
        # Retrieve and rerank chunks
        retrieved_chunks = hybrid_search(rewritten_query, conversation_id)
        reranked_chunks = rerank_chunks(rewritten_query, retrieved_chunks)
        
        # Build context from chunks
        context_parts = []
        
        for idx, chunk in enumerate(reranked_chunks):
            context_parts.append(f"[Source {idx + 1}]: {chunk['text']}")
            sources.append({
                "filename": chunk["metadata"].get("filename", "Unknown"),
                "page_number": chunk["metadata"].get("page_number"),
                "chunk_index": chunk["metadata"].get("chunk_index"),
                "score": chunk.get("rerank_score", chunk.get("score", 0))
            })
        
        context_str = "\n\n".join(context_parts)
        
        # Build RAG prompt
        prompt = (
            "You are a helpful assistant that answers questions based on the provided context from uploaded documents.\n\n"
            f"Context from documents:\n{context_str}\n\n"
            f"Question: {user_message}\n\n"
            "Instructions:\n"
            "- Answer ONLY using the provided context\n"
            "- If the answer is not in the context, say 'I couldn't find this information in the uploaded documents'\n"
            "- Include source citations in your answer using [Source X] format\n"
            "- Be concise and accurate\n"
        )
    else:
        # Normal chat without RAG
        conversation = []
        for msg in history:
            conversation.append(f"{msg['role']}: {msg['content']}")
        conversation.append(f"user: {user_message}")
        
        prompt = "\n".join(conversation)
    
    full_reply = ""
    
    try:
        # Generate streaming response
        response = model.generate_content(prompt, stream=True)
        
        for chunk in response:
            if await request.is_disconnected():
                print('Client disconnected, stopping stream')
                break
                
            if chunk.text:
                token = chunk.text
                full_reply += token
                yield token
        
        yield "\n"
        
        # Send sources as metadata if RAG is enabled
        if use_rag and sources:
            import json
            yield f"__SOURCES__:{json.dumps(sources)}\n"
        
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

    


