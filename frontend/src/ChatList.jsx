import { useState } from 'react'

function Sources({ sources }) {
  const [expanded, setExpanded] = useState(false)

  if (!sources || sources.length === 0) {
    return null
  }

  return (
    <div className="sources">
      <button 
        className="sources-toggle" 
        onClick={() => setExpanded(!expanded)}
      >
        {expanded ? '▼' : '▶'} Sources ({sources.length})
      </button>
      {expanded && (
        <ul className="sources-list">
          {sources.map((source, idx) => (
            <li key={idx} className="source-item">
              <span className="source-filename">{source.filename}</span>
              {source.page_number && (
                <span className="source-page">Page {source.page_number}</span>
              )}
              <span className="source-score">
                {(source.score * 100).toFixed(1)}%
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export default function ChatList({chats}){
    return(
        <div>
            {chats.map((chat)=>(
                <div key={chat._id} className={`message ${chat.role}`}>
                    <p>{chat.reply}</p>
                    {chat.sources && <Sources sources={chat.sources} />}
                </div>
                   
            ))}
        </div>
    )
}