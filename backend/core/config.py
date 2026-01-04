from dotenv import load_dotenv
import os


load_dotenv()
OPENAI_API_KEY=os.getenv('OPENAI_API_KEY')
MEMORY_LIMIT=10
MONGODB_URL=os.getenv("MONGODB_URL")