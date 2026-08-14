import { useEffect, useRef } from 'react'
import './App.css'
import './main.css'

import ChatList from './ChatList'
import ChatInput from './ChatInput'
import UseChats from './UseChats'
import ConversationList from './ConversationList'
import DocumentUpload from './DocumentUpload'
import DocumentList from './DocumentList'

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
    switchConversation,
    documents,
    useRag,
    setUseRag,
    handleDocumentUpload,
    handleDocumentDelete
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
        {activeConversationId && (
          <>
            <DocumentUpload
              conversationId={activeConversationId}
              onUploadSuccess={handleDocumentUpload}
            />
            <DocumentList
              documents={documents}
              onDeleteDocument={handleDocumentDelete}
            />
          </>
        )}
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
            useRag={useRag}
            onToggleRag={() => setUseRag(!useRag)}
          />
        </footer>
      </main>
    </div>
  )
}

export default App