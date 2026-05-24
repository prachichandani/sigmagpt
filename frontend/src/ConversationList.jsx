import { useState } from 'react';

export default function ConversationList({
  conversations,
  activeConversationId,
  onCreateConversation,
  onDeleteConversation,
  onSwitchConversation
}) {
  const [isHovered, setIsHovered] = useState(null);

  return (
    <div className="conversation-list">
      <div className="conversation-header">
        <h3>Conversations</h3>
        <button 
          className="new-chat-btn"
          onClick={() => onCreateConversation()}
        >
          + New Chat
        </button>
      </div>
      
      <div className="conversations">
        {conversations.length === 0 ? (
          <div className="no-conversations">
            <p>No conversations yet</p>
            <button onClick={() => onCreateConversation()}>
              Start a new conversation
            </button>
          </div>
        ) : (
          conversations.map((conversation) => (
            <div
              key={conversation._id}
              className={`conversation-item ${
                conversation._id === activeConversationId ? 'active' : ''
              }`}
              onClick={() => onSwitchConversation(conversation._id)}
              onMouseEnter={() => setIsHovered(conversation._id)}
              onMouseLeave={() => setIsHovered(null)}
            >
              <div className="conversation-title">
                {conversation.title}
              </div>
              {isHovered === conversation._id && (
                <button
                  className="delete-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteConversation(conversation._id);
                  }}
                >
                  ×
                </button>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
