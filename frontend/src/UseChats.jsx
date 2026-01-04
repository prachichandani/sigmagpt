import { useState ,useEffect,useRef} from 'react'
import {fetchchatsapi,sendmessageapi,clearconversationapi,sendmessagestreamapi} from './api'
export default function UseChats(){
    const [chats,setChats]= useState([]);
    const [error, setError]= useState(null);
    const [loading,setLoading]=useState(false);
    const abortRef=useRef(null);

    const fetchchats=async()=>{
    try{
      setLoading(true); setError(null);
      const data = await fetchchatsapi();
      console.log('fetched',data)
      setChats(data)
      console.log(data)
    }catch(err){
      setError(err.message)
    }finally{
      setLoading(false)
    } 
    }
  useEffect(()=>{
    fetchchats()
  },[])

  const sendmessage=async(text)=>{
    try{
      setLoading(true); setError(null);
      await sendmessageapi(text)
     await fetchchats();
    }catch(err){
      setError(err.message)
    }finally{
      setLoading(false);
    }
    
    
  }

  const sendmessagestream = async (text) => {
  abortRef.current= new AbortController();
  const assistantId = crypto.randomUUID();
  try {
    setLoading(true);
    setError(null);
    
    setChats((prev) => [
      ...prev,
      { _id: crypto.randomUUID(), role: "user", reply: text },
      {_id: assistantId, role: "assistant", reply: '' }
    ]);
   
    const stream = await sendmessagestreamapi(text,abortRef.current.signal);
    const reader = stream.getReader();
    const decoder = new TextDecoder();

    let aiReply = "";

   
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      aiReply += chunk;

      
      setChats((prev)=>(
        prev.map((m)=>(
          m._id===assistantId?{...m,reply:aiReply}:m
        ))
      ))
    }

  } catch (err) {
    if(err.name!='AbortError'){
      setError(err.message);
    }
    
  } finally {
    setLoading(false);
  }
};



  const clearconversation = async()=>{
    try{
      await clearconversationapi()
      await fetchchats()
    }catch(err){
      setError(err.message)
    }finally{
      setLoading(false)
    }
    
  }
  const stopgenerating=()=>{
    abortRef.current?.abort();
  }
    return{
        chats, 
        loading,
        error,
        sendmessage,
        clearconversation,
        sendmessagestream,
        stopgenerating
    }
}