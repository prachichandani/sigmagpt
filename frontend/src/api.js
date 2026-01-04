const base =  import.meta.env.VITE_API_BASE_URL;

export const fetchchatsapi=async()=>{
   const res = await fetch(`${base}/chats`)
      if(!res.ok){
        throw new Error('Failed to fetch chats');
      }
      return  res.json()
}

export const sendmessageapi= async(text)=>{
     const res = await fetch(`${base}/chat`,{
      method  :'POST',
      headers:{ "Content-Type": "application/json"},
      body: JSON.stringify({message:text})
    })
    if(!res.ok){
      throw new Error('Failed to send message')
    }
}
export const sendmessagestreamapi = async (text,signal) => {
  const res = await fetch(`${base}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: text }),
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