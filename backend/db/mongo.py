from pymongo import MongoClient
from core.config import MONGODB_URL


client = MongoClient(MONGODB_URL)
db = client['sigmagpt']
chats_collection = db["chats"]
conversations_collection = db["conversations"]
documents_collection = db["documents"]
rag_logs_collection = db["rag_logs"]

