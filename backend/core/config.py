from dotenv import load_dotenv
import os


load_dotenv()
GEMINI_API_KEY=os.getenv('GEMINI_API_KEY')
MEMORY_LIMIT=10
MONGODB_URL=os.getenv("MONGODB_URL")
EMBEDDING_MODEL_NAME=os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")