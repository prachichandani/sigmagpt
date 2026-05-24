import { useState ,useEffect,useRef} from 'react'
import {fetchchatsapi,sendmessageapi,clearconversationapi,sendmessagestreamapi,createConversation,getConversations,deleteConversation} from './api'
export default function UseChats(){
    const [chats,setChats]= useState([]);
    const [conversations,setConversations]= useState([]);
    const [activeConversationId,setActiveConversationId]= useState(null);
    const [error, setError]= useState(null);
    const [loading,setLoading]=useState(false);
    const abortRef=useRef(null);

    const fetchchats=async()=>{
    try{
      setLoading(true); setError(null);
      const data = await fetchchatsapi(activeConversationId);
      console.log('fetched',data)
      setChats(data)
      console.log(data)
    }catch(err){
      setError(err.message)
    }finally{
      setLoading(false)
    }
    }

    const fetchConversations = async ()=>{
      try{
        const data = await getConversations();
        setConversations(data);
        // If no active conversation and conversations exist, set the first one as active
        if (!activeConversationId && data.length > 0) {
          setActiveConversationId(data[0]._id);
        }
      }catch(err){
        setError(err.message)
      }
    }

  useEffect(()=>{
    fetchConversations();
  },[])

  useEffect(()=>{
    if(activeConversationId){
      fetchchats()
    }
  },[activeConversationId])

  const sendmessage=async(text)=>{
    if(!activeConversationId){
      setError('No active conversation selected');
      return;
    }
    try{
      setLoading(true); setError(null);
      await sendmessageapi(text, activeConversationId)
     await fetchchats();
     await fetchConversations(); // Refresh to get updated title and move to top
    }catch(err){
      setError(err.message)
    }finally{
      setLoading(false);
    }


  }

  const sendmessagestream = async (text) => {
  if(!activeConversationId){
    setError('No active conversation selected');
    return;
  }
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

    const stream = await sendmessagestreamapi(text, activeConversationId, abortRef.current.signal);
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

    // Refresh conversations to get updated title
    await fetchConversations();

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

  const handleCreateConversation = async (firstMessage = null) => {
    try{
      setLoading(true); setError(null);
      const newConversation = await createConversation(firstMessage);
      setConversations([newConversation, ...conversations]);
      setActiveConversationId(newConversation._id);
    }catch(err){
      setError(err.message)
    }finally{
      setLoading(false)
    }
  }

  const handleDeleteConversation = async (conversationId) => {
    try{
      setLoading(true); setError(null);
      await deleteConversation(conversationId);
      const updated = conversations.filter(c => c._id !== conversationId);
      setConversations(updated);
      if(activeConversationId === conversationId){
        setActiveConversationId(updated.length > 0 ? updated[0]._id : null);
        setChats([]);
      }
    }catch(err){
      setError(err.message)
    }finally{
      setLoading(false)
    }
  }

  const switchConversation = (conversationId) => {
    setActiveConversationId(conversationId);
    // Move active conversation to top of list locally
    const activeConv = conversations.find(c => c._id === conversationId);
    if (activeConv) {
      const otherConvs = conversations.filter(c => c._id !== conversationId);
      setConversations([activeConv, ...otherConvs]);
    }
  }

  const stopgenerating=()=>{
    abortRef.current?.abort();
  }
    return{
        chats,
        conversations,
        activeConversationId,
        loading,
        error,
        sendmessage,
        clearconversation,
        sendmessagestream,
        stopgenerating,
        createConversation: handleCreateConversation,
        deleteConversation: handleDeleteConversation,
        switchConversation,
        fetchConversations
    }
}