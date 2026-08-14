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

export const sendmessageapi= async(text, conversationId, useRag = false)=>{
     const res = await fetch(`${base}/chat`,{
      method  :'POST',
      headers:{ "Content-Type": "application/json"},
      body: JSON.stringify({message:text, conversation_id:conversationId, use_rag: useRag})
    })
    if(!res.ok){
      throw new Error('Failed to send message')
    }
}
export const sendmessagestreamapi = async (text, conversationId, signal, useRag = false) => {
  const res = await fetch(`${base}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: text, conversation_id: conversationId, use_rag: useRag }),
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

export const uploadDocument = async (conversationId, file, fileType = null) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('conversation_id', conversationId);
  if (fileType) {
    formData.append('file_type', fileType);
  }
  
  const res = await fetch(`${base}/documents/upload`, {
    method: 'POST',
    body: formData
  });
  
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Failed to upload document' }));
    throw new Error(error.detail || 'Failed to upload document');
  }
  
  return res.json();
};

export const getDocuments = async (conversationId) => {
  const res = await fetch(`${base}/documents/${encodeURIComponent(conversationId)}`);
  
  if (!res.ok) {
    throw new Error('Failed to fetch documents');
  }
  
  return res.json();
};

export const deleteDocument = async (documentId, conversationId) => {
  const res = await fetch(`${base}/documents/${encodeURIComponent(documentId)}?conversation_id=${encodeURIComponent(conversationId)}`, {
    method: 'DELETE'
  });
  
  if (!res.ok) {
    throw new Error('Failed to delete document');
  }
  
  return res.json();
};