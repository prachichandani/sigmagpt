from dotenv import load_dotenv
import os


load_dotenv()
GEMINI_API_KEY=os.getenv('GEMINI_API_KEY')
MEMORY_LIMIT=10
MONGODB_URL=os.getenv("MONGODB_URL")
EMBEDDING_MODEL_NAME=os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

# RAG Configuration
CHROMA_DB_PATH=os.getenv("CHROMA_DB_PATH", "./chroma_db")
MAX_FILE_SIZE_MB=int(os.getenv("MAX_FILE_SIZE_MB", "10"))
ALLOWED_FILE_TYPES=["PDF", "TXT"]
CHUNK_SIZE=int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP=int(os.getenv("CHUNK_OVERLAP", "200"))
RETRIEVAL_TOP_K=int(os.getenv("RETRIEVAL_TOP_K", "20"))
FINAL_CONTEXT_TOP_K=int(os.getenv("FINAL_CONTEXT_TOP_K", "5"))
RERANKER_MODEL_NAME = os.getenv(
    "RERANKER_MODEL_NAME",
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)