import google.generativeai as genai
import numpy as np
from typing import List
from core.config import GEMINI_API_KEY, EMBEDDING_MODEL_NAME

class EmbeddingGenerator:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = EMBEDDING_MODEL_NAME
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        result = genai.embed_content(
            model=self.model,
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        embeddings = []
        for text in texts:
            embedding = self.generate_embedding(text)
            embeddings.append(embedding)
        return embeddings
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        emb1 = np.array(embedding1)
        emb2 = np.array(embedding2)
        
        cosine_sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        return float(cosine_sim)

# Global instance
embedding_generator = EmbeddingGenerator()
