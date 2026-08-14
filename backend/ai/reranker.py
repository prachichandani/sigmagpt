from typing import List, Dict, Optional
from sentence_transformers import CrossEncoder
from core.config import FINAL_CONTEXT_TOP_K, RERANKER_MODEL_NAME


class Reranker:
    """
    Rerank retrieved chunks using a cross-encoder for better relevance.

    Architecture:
    - Hybrid search retrieves candidate chunks.
    - Cross-encoder scores query-chunk pairs more accurately.
    - Top-k chunks are sent to the LLM as final context.
    """

    def __init__(self, model_name: Optional[str] = None):
        try:
            self.model_name = model_name or RERANKER_MODEL_NAME
            self.model = CrossEncoder(self.model_name)
        except Exception as e:
            raise RuntimeError(f"Failed to load cross-encoder model: {str(e)}")

    def rerank(
        self,
        query: str,
        chunks: List[Dict],
        top_k: int = FINAL_CONTEXT_TOP_K,
        max_chars_per_chunk: int = 1500
    ) -> List[Dict]:
        if not query or not query.strip():
            return chunks[:top_k]

        if not chunks:
            return []

        safe_chunks = [chunk.copy() for chunk in chunks]

        query_doc_pairs = [
            (query, chunk.get("text", "")[:max_chars_per_chunk])
            for chunk in safe_chunks
        ]

        try:
            rerank_scores = self.model.predict(query_doc_pairs)
        except Exception as e:
            print(f"Reranking error: {str(e)}")

            for chunk in safe_chunks:
                chunk["rerank_score"] = 0.0

            return safe_chunks[:top_k]

        for idx, chunk in enumerate(safe_chunks):
            chunk["rerank_score"] = float(rerank_scores[idx])

        reranked_chunks = sorted(
            safe_chunks,
            key=lambda x: x["rerank_score"],
            reverse=True
        )

        return reranked_chunks[:top_k]


_reranker_instance = None


def get_reranker() -> Reranker:
    global _reranker_instance

    if _reranker_instance is None:
        _reranker_instance = Reranker()

    return _reranker_instance


def rerank_chunks(
    query: str,
    chunks: List[Dict],
    top_k: int = FINAL_CONTEXT_TOP_K
) -> List[Dict]:
    reranker = get_reranker()
    return reranker.rerank(query, chunks, top_k)