# SigmaGPT - RAG-Powered AI Chat Application

A modern chat application with Retrieval-Augmented Generation (RAG) capabilities, allowing users to upload documents and get AI responses based on their content.

## Features

- **AI Chat Interface**: Clean, responsive chat UI with streaming responses
- **Document Upload**: Upload PDF and TXT files for context-aware responses
- **RAG Toggle**: Enable/disable retrieval-augmented generation per conversation
- **Source Citations**: View document sources used in AI responses with relevance scores
- **Conversation Management**: Create, switch, and delete multiple conversations
- **Real-time Streaming**: Fast, streaming AI responses using Gemini API
- **Document Management**: View and delete uploaded documents per conversation

## Tech Stack

### Backend
- **FastAPI**: Python web framework
- **MongoDB**: Document storage for conversations, chats, and document metadata
- **ChromaDB**: Vector database for semantic search
- **Sentence Transformers**: Text embeddings (all-MiniLM-L6-v2)
- **Cross Encoder**: Reranking model (ms-marco-MiniLM-L-6-v2)
- **Google Gemini**: LLM for chat and query rewriting
- **BM25**: Keyword search implementation

### Frontend
- **React**: UI framework
- **Vite**: Build tool
- **CSS**: Custom styling with dark theme

## Project Structure

```
sigmagpt/
├── backend/
│   ├── ai/
│   │   ├── chunker.py          # Text chunking with overlap
│   │   ├── embeddings.py       # Embedding generation
│   │   ├── llm.py              # LLM integration and RAG logic
│   │   ├── rag.py              # Document processing and retrieval
│   │   └── reranker.py         # Cross-encoder reranking
│   ├── core/
│   │   └── config.py           # Configuration settings
│   ├── db/
│   │   └── mongo.py            # MongoDB connection
│   ├── routes/
│   │   ├── chat.py             # Chat endpoints
│   │   └── documents.py        # Document upload/management
│   ├── main.py                 # FastAPI app entry point
│   ├── requirements.txt        # Python dependencies
│   └── .env                    # Environment variables
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main app component
│   │   ├── ChatInput.jsx       # Message input with RAG toggle
│   │   ├── ChatList.jsx        # Chat messages with sources
│   │   ├── ConversationList.jsx # Conversation sidebar
│   │   ├── DocumentUpload.jsx  # File upload component
│   │   ├── DocumentList.jsx    # Document list display
│   │   ├── UseChats.jsx        # Custom hook for chat logic
│   │   ├── api.js              # API client functions
│   │   └── App.css             # Component styling
│   └── package.json            # Node dependencies
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB instance
- Google Gemini API key

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file with the following variables:
```env
GEMINI_API_KEY=your_gemini_api_key
MONGODB_URL=mongodb://localhost:27017
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
CHROMA_DB_PATH=./chroma_db
MAX_FILE_SIZE_MB=10
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
RETRIEVAL_TOP_K=20
FINAL_CONTEXT_TOP_K=5
RERANKER_MODEL_NAME=cross-encoder/ms-marco-MiniLM-L-6-v2
```

5. Start the backend server:
```bash
python main.py
```

The backend will run on `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file with the API base URL:
```env
VITE_API_BASE_URL=http://localhost:8000
```

4. Start the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:5173`

## Usage

### Basic Chat
1. Open the application in your browser
2. Create a new conversation or select an existing one
3. Type your message and press Send
4. The AI will respond in real-time with streaming text

### Using RAG (Document-Based Chat)

1. **Upload Documents**:
   - Click the file input in the sidebar
   - Select a PDF or TXT file
   - Click Upload to process the document
   - The document will be chunked, embedded, and stored

2. **Enable RAG**:
   - Toggle the RAG switch in the chat input area
   - When enabled, the AI will use uploaded documents for context

3. **Chat with Documents**:
   - Ask questions about your uploaded documents
   - The AI will retrieve relevant chunks and provide answers
   - Sources will be displayed below the response showing:
     - Filename
     - Page number (for PDFs)
     - Relevance score

4. **Manage Documents**:
   - View all uploaded documents in the sidebar
   - Delete documents using the × button
   - Documents are scoped per conversation

### Conversation Management
- Click "New Conversation" to start fresh
- Click on conversations in the sidebar to switch between them
- Delete conversations using the delete button
- Conversations are automatically titled based on the first message

## RAG Pipeline

The RAG system implements a sophisticated retrieval pipeline:

1. **Document Processing**:
   - PDF/TXT text extraction
   - Recursive separator-based chunking
   - Configurable chunk size and overlap
   - Metadata preservation (page numbers, chunk indices)

2. **Embedding Generation**:
   - SentenceTransformer embeddings (all-MiniLM-L6-v2)
   - Cosine similarity for semantic search
   - Batch processing for efficiency

3. **Hybrid Retrieval**:
   - Semantic search using ChromaDB
   - Keyword search using BM25
   - Reciprocal Rank Fusion (RRF) for result merging

4. **Reranking**:
   - Cross-encoder reranking (ms-marco-MiniLM-L-6-v2)
   - Query-chunk pair scoring
   - Top-k selection for final context

5. **Query Enhancement**:
   - Conversation history analysis
   - Query rewriting for better retrieval
   - Context-aware follow-up handling

6. **Response Generation**:
   - Context injection into prompts
   - Source citation formatting
   - Streaming responses with metadata

## API Endpoints

### Chat
- `POST /chat` - Send message (non-streaming)
- `POST /chat/stream` - Send message (streaming)
- `GET /chats?conversation_id={id}` - Get conversation messages
- `DELETE /chats` - Clear all messages
- `DELETE /chat/{chat_id}` - Delete specific message

### Conversations
- `POST /conversations` - Create new conversation
- `GET /conversations` - List all conversations
- `DELETE /conversations/{id}` - Delete conversation

### Documents
- `POST /documents/upload` - Upload document
- `GET /documents/{conversation_id}` - List documents
- `DELETE /documents/{document_id}?conversation_id={id}` - Delete document

## Configuration

Key configuration options in `backend/core/config.py`:

- `CHUNK_SIZE`: Maximum characters per chunk (default: 1000)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200)
- `RETRIEVAL_TOP_K`: Number of chunks to retrieve (default: 20)
- `FINAL_CONTEXT_TOP_K`: Number of chunks after reranking (default: 5)
- `MAX_FILE_SIZE_MB`: Maximum upload file size (default: 10)
- `MEMORY_LIMIT`: Conversation history limit (default: 10)

## Troubleshooting

### Common Issues

1. **MongoDB Connection Error**:
   - Ensure MongoDB is running
   - Check `MONGODB_URL` in `.env`

2. **Embedding Model Download**:
   - First run will download models automatically
   - Ensure internet connection on first startup

3. **File Upload Fails**:
   - Check file size (max 10MB by default)
   - Ensure file is PDF or TXT format
   - Check file has extractable text

4. **RAG Returns No Results**:
   - Ensure documents are uploaded
   - Check if RAG toggle is enabled
   - Verify query is relevant to document content

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
