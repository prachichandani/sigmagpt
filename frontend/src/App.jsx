import { useState ,useEffect,useRef} from 'react'
// import reactLogo from './assets/react.svg'
// import viteLogo from '/vite.svg'
import './App.css'
import ChatList from './ChatList'
import ChatInput from './ChatInput'
import UseChats from './UseChats'
import './main.css'

function App() {
  const bottomRef=useRef();
  const{
    chats,loading,error,sendmessage,clearconversation,sendmessagestream,stopgenerating
  }=UseChats()

  useEffect(()=>{
    bottomRef.current?.scrollIntoView({behavior:'smooth'})
  },[chats])



  return (
    <div className='app'>
      <h1 className='header' >SIGMA GPT</h1>
      <main className='chat-container'>
        <div  className='chat-scroll'>
        {loading && <p className='typing' >AI is typing</p>}
        {error && <p className='error'>{error}</p>}
        <ChatList chats={chats}/>
        <div ref={bottomRef} />
        </div>
      </main>
      <footer className='input-container'>
        <ChatInput onsend={sendmessagestream} onclear={clearconversation} onstop={stopgenerating} loading={loading}/>
      </footer>
    </div>
  )
}

export default App
