import { useEffect, useRef } from 'react'
import './App.css'
import './main.css'

import ChatList from './ChatList'
import ChatInput from './ChatInput'
import UseChats from './UseChats'
import ConversationList from './ConversationList'

function App() {
  const bottomRef = useRef()

  const {
    chats,
    conversations,
    activeConversationId,
    loading,
    error,
    clearconversation,
    sendmessagestream,
    stopgenerating,
    createConversation,
    deleteConversation,
    switchConversation
  } = UseChats()

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chats])

  return (
    <div className="app">
      <aside className="sidebar">
        <ConversationList
          conversations={conversations}
          activeConversationId={activeConversationId}
          onCreateConversation={createConversation}
          onDeleteConversation={deleteConversation}
          onSwitchConversation={switchConversation}
        />
      </aside>

      <main className="chat-container">
        <h1 className="header">SIGMA GPT</h1>

        <div className="chat-scroll">
          {loading && <p className="typing">AI is typing</p>}
          {error && <p className="error">{error}</p>}

          <ChatList chats={chats} />
          <div ref={bottomRef} />
        </div>

        <footer className="input-container">
          <ChatInput
            onsend={sendmessagestream}
            onclear={clearconversation}
            onstop={stopgenerating}
            loading={loading}
          />
        </footer>
      </main>
    </div>
  )
}

export default App