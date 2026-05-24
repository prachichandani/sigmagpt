const base =  import.meta.env.VITE_API_BASE_URL;

export const fetchchatsapi=async(conversationId)=>{
   const url = conversationId 
     ? `${base}/chats?conversation_id=${encodeURIComponent(conversationId)}`
     : `${base}/chats`;
   const res = await fetch(url)
      if(!res.ok){
        throw new Error('Failed to fetch chats');
      }
      return  res.json()
}

export const sendmessageapi= async(text, conversationId)=>{
     const res = await fetch(`${base}/chat`,{
      method  :'POST',
      headers:{ "Content-Type": "application/json"},
      body: JSON.stringify({message:text, conversation_id:conversationId})
    })
    if(!res.ok){
      throw new Error('Failed to send message')
    }
}
export const sendmessagestreamapi = async (text, conversationId, signal) => {
  const res = await fetch(`${base}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: text, conversation_id: conversationId }),
    signal
  });
  if(!res.ok){
      throw new Error('Failed to send message')
    }

  return res.body;
};

export const clearconversationapi=async()=>{
    const res =await  fetch(`${base}/chats`,{
      method:'DELETE'
      })
      if(!res.ok){
        throw new Error('Failed to clear conversation')
      }
}

export const createConversation = async (firstMessage = null) => {
  const url = firstMessage 
    ? `${base}/conversations?first_message=${encodeURIComponent(firstMessage)}`
    : `${base}/conversations`;
  
  const res = await fetch(url, {
    method: 'POST'
  });
  
  if (!res.ok) {
    throw new Error('Failed to create conversation');
  }
  
  return res.json();
};

export const getConversations = async () => {
  const res = await fetch(`${base}/conversations`);
  
  if (!res.ok) {
    throw new Error('Failed to fetch conversations');
  }
  
  return res.json();
};

export const deleteConversation = async (conversationId) => {
  const res = await fetch(`${base}/conversations/${encodeURIComponent(conversationId)}`, {
    method: 'DELETE'
  });
  
  if (!res.ok) {
    throw new Error('Failed to delete conversation');
  }
  
  return res.json();
};