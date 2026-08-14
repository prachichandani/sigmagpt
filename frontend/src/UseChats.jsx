import { useState ,useEffect,useRef} from 'react'
import {fetchchatsapi,sendmessageapi,clearconversationapi,sendmessagestreamapi,createConversation,getConversations,deleteConversation,getDocuments,deleteDocument} from './api'
export default function UseChats(){
    const [chats,setChats]= useState([]);
    const [conversations,setConversations]= useState([]);
    const [activeConversationId,setActiveConversationId]= useState(null);
    const [error, setError]= useState(null);
    const [loading,setLoading]=useState(false);
    const abortRef=useRef(null);
    const [documents, setDocuments] = useState([]);
    const [useRag, setUseRag] = useState(false);

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
      fetchDocuments()
    }
  },[activeConversationId])

  const fetchDocuments = async () => {
    if (!activeConversationId) return
    try {
      const data = await getDocuments(activeConversationId)
      setDocuments(data.data || [])
    } catch (err) {
      console.error('Failed to fetch documents:', err)
    }
  }

  const sendmessage=async(text)=>{
    if(!activeConversationId){
      setError('No active conversation selected');
      return;
    }
    try{
      setLoading(true); setError(null);
      await sendmessageapi(text, activeConversationId, useRag)
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

    const stream = await sendmessagestreamapi(text, activeConversationId, abortRef.current.signal, useRag);
    const reader = stream.getReader();
    const decoder = new TextDecoder();

    let aiReply = "";
    let sources = null;


    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      
      // Check for sources metadata
      if (chunk.includes('__SOURCES__:')) {
        const parts = chunk.split('__SOURCES__:');
        aiReply += parts[0];
        if (parts[1]) {
          try {
            sources = JSON.parse(parts[1].trim());
          } catch (e) {
            console.error('Failed to parse sources:', e);
          }
        }
      } else {
        aiReply += chunk;
      }

      setChats((prev)=>(
        prev.map((m)=>(
          m._id===assistantId?{...m,reply:aiReply, sources: sources}:m
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

  const handleDocumentUpload = async (uploadedDoc) => {
    setDocuments(prev => [...prev, uploadedDoc])
  }

  const handleDocumentDelete = async (documentId) => {
    try {
      await deleteDocument(documentId, activeConversationId)
      setDocuments(prev => prev.filter(doc => doc._id !== documentId))
    } catch (err) {
      setError(err.message)
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
        fetchConversations,
        documents,
        useRag,
        setUseRag,
        handleDocumentUpload,
        handleDocumentDelete
    }
}