import chromadb
from pypdf import PdfReader
from typing import List, Dict
from bson import ObjectId
from datetime import datetime, timezone
from io import BytesIO
from ai.chunker import chunk_text
from ai.embeddings import embedding_generator
from core.config import (
    CHROMA_DB_PATH,
    MAX_FILE_SIZE_MB,
    ALLOWED_FILE_TYPES,
    RETRIEVAL_TOP_K
)
from db.mongo import documents_collection
from rank_bm25 import BM25Okapi


# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)


def extract_text_from_pdf(file_bytes: bytes) -> List[Dict]:
    """
    Extract text from PDF file bytes with page numbers.
    
    Returns:
        List of dicts with 'page_number' and 'text' keys
    """
    try:
        reader = PdfReader(BytesIO(file_bytes))
        pages_text = []

        for page_num, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            if page_text.strip():
                pages_text.append({
                    "page_number": page_num,
                    "text": page_text.strip()
                })

        return pages_text

    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")


def extract_text_from_txt(file_bytes: bytes) -> str:
    """
    Extract text from TXT file bytes.
    """
    try:
        return file_bytes.decode("utf-8").strip()
    except UnicodeDecodeError:
        try:
            return file_bytes.decode("latin-1").strip()
        except Exception as e:
            raise ValueError(f"Failed to decode text file: {str(e)}")


def process_document(
    file_bytes: bytes,
    filename: str,
    conversation_id: str,
    file_type: str
) -> Dict:
    """
    Process uploaded document:
    extract text, chunk, generate embeddings, store in ChromaDB,
    and save metadata in MongoDB.
    """
    file_type = file_type.upper()

    if file_type not in ALLOWED_FILE_TYPES:
        raise ValueError(f"Unsupported file type: {file_type}")

    file_size_mb = len(file_bytes) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise ValueError(f"File size exceeds maximum of {MAX_FILE_SIZE_MB}MB")

    if file_type == "PDF":
        pages = extract_text_from_pdf(file_bytes)
        if not pages:
            raise ValueError("PDF is empty or contains no extractable text")
        
        # Chunk each page separately with page number
        chunks = []
        for page_data in pages:
            page_chunks = chunk_text(page_data["text"], page_number=page_data["page_number"])
            chunks.extend(page_chunks)
    elif file_type == "TXT":
        text = extract_text_from_txt(file_bytes)
        if not text or len(text.strip()) < 10:
            raise ValueError("Document is empty or contains too little text")
        chunks = chunk_text(text)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

    if not chunks:
        raise ValueError("Failed to chunk document")

    document_id = str(ObjectId())
    collection_name = f"conversation_{conversation_id}"

    try:
        collection = chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    except Exception as e:
        raise ValueError(f"Failed to create ChromaDB collection: {str(e)}")

    chunk_texts = [chunk["text"] for chunk in chunks]
    embeddings = embedding_generator.generate_embeddings(chunk_texts)

    metadatas = []
    ids = []

    for idx, chunk in enumerate(chunks):
        metadatas.append({
            "conversation_id": conversation_id,
            "document_id": document_id,
            "filename": filename,
            "page_number": chunk.get("page_number"),
            "chunk_index": chunk["chunk_index"],
            "file_type": file_type,
            "chunk_type": chunk.get("chunk_type"),
            "chunk_size": chunk.get("chunk_size"),
            "chunk_overlap": chunk.get("chunk_overlap")
        })

        ids.append(f"{document_id}_chunk_{idx}")

    try:
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunk_texts,
            metadatas=metadatas
        )
    except Exception as e:
        raise ValueError(f"Failed to store chunks in ChromaDB: {str(e)}")

    document_metadata = {
        "_id": ObjectId(document_id),
        "conversation_id": ObjectId(conversation_id),
        "filename": filename,
        "file_type": file_type,
        "file_size": len(file_bytes),
        "uploaded_at": datetime.now(timezone.utc),
        "total_chunks": len(chunks),
        "status": "processed"
    }

    try:
        documents_collection.insert_one(document_metadata)
    except Exception as e:
        try:
            collection.delete(ids=ids)
        except Exception:
            pass

        raise ValueError(f"Failed to save document metadata: {str(e)}")

    return {
        "document_id": document_id,
        "filename": filename,
        "file_type": file_type,
        "file_size": len(file_bytes),
        "total_chunks": len(chunks),
        "status": "processed"
    }


def delete_document(document_id: str, conversation_id: str) -> Dict:
    """
    Delete document metadata from MongoDB and chunks from ChromaDB.
    """
    try:
        document_object_id = ObjectId(document_id)
    except Exception:
        raise ValueError("Invalid document ID")

    document = documents_collection.find_one({"_id": document_object_id})

    if not document:
        raise ValueError("Document not found")

    collection_name = f"conversation_{conversation_id}"

    try:
        collection = chroma_client.get_collection(name=collection_name)

        chunks = collection.get(
            where={"document_id": document_id}
        )

        if chunks and chunks.get("ids"):
            collection.delete(ids=chunks["ids"])

    except Exception as e:
        raise ValueError(f"Failed to delete chunks from ChromaDB: {str(e)}")

    try:
        documents_collection.delete_one({"_id": document_object_id})
    except Exception as e:
        raise ValueError(f"Failed to delete document metadata: {str(e)}")

    return {"message": "Document deleted successfully"}


def get_conversation_documents(conversation_id: str) -> List[Dict]:
    """
    Get all uploaded documents for a conversation.
    """
    try:
        conversation_object_id = ObjectId(conversation_id)

        documents = list(
            documents_collection.find(
                {"conversation_id": conversation_object_id}
            ).sort("uploaded_at", -1)
        )

        for doc in documents:
            doc["_id"] = str(doc["_id"])
            doc["conversation_id"] = str(doc["conversation_id"])

        return documents

    except Exception as e:
        raise ValueError(f"Failed to get documents: {str(e)}")


def semantic_search(
    query: str,
    conversation_id: str,
    top_k: int = RETRIEVAL_TOP_K
) -> List[Dict]:
    """
    Perform semantic search using ChromaDB.
    """
    try:
        collection_name = f"conversation_{conversation_id}"
        collection = chroma_client.get_collection(name=collection_name)

        query_embedding = embedding_generator.generate_embedding(query)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"conversation_id": conversation_id}
        )

        chunks = []

        if results and results.get("ids") and results["ids"][0]:
            for idx, chunk_id in enumerate(results["ids"][0]):
                chunks.append({
                    "chunk_id": chunk_id,
                    "text": results["documents"][0][idx],
                    "metadata": results["metadatas"][0][idx],
                    "score": results["distances"][0][idx]
                    if results.get("distances") else 0.0,
                    "retrieval_type": "semantic"
                })

        return chunks

    except Exception as e:
        print(f"Semantic search error: {str(e)}")
        return []


def keyword_search(
    query: str,
    conversation_id: str,
    top_k: int = RETRIEVAL_TOP_K
) -> List[Dict]:
    """
    Perform keyword search using BM25.
    """
    try:
        collection_name = f"conversation_{conversation_id}"
        collection = chroma_client.get_collection(name=collection_name)

        all_results = collection.get(
            where={"conversation_id": conversation_id}
        )

        if not all_results or not all_results.get("documents"):
            return []

        tokenized_corpus = [
            doc.lower().split()
            for doc in all_results["documents"]
        ]

        bm25 = BM25Okapi(tokenized_corpus)

        tokenized_query = query.lower().split()
        doc_scores = bm25.get_scores(tokenized_query)

        top_indices = sorted(
            range(len(doc_scores)),
            key=lambda i: doc_scores[i],
            reverse=True
        )[:top_k]

        chunks = []

        for idx in top_indices:
            chunks.append({
                "chunk_id": all_results["ids"][idx],
                "text": all_results["documents"][idx],
                "metadata": all_results["metadatas"][idx],
                "score": float(doc_scores[idx]),
                "retrieval_type": "keyword"
            })

        return chunks

    except Exception as e:
        print(f"Keyword search error: {str(e)}")
        return []


def reciprocal_rank_fusion(
    semantic_results: List[Dict],
    keyword_results: List[Dict],
    k: int = 60
) -> List[Dict]:
    """
    Merge semantic and keyword search results using Reciprocal Rank Fusion.
    """
    rrf_scores = {}
    chunk_data = {}

    for rank, result in enumerate(semantic_results):
        chunk_id = result["chunk_id"]
        rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + 1 / (k + rank + 1)
        chunk_data[chunk_id] = result

    for rank, result in enumerate(keyword_results):
        chunk_id = result["chunk_id"]
        rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + 1 / (k + rank + 1)

        if chunk_id in chunk_data:
            chunk_data[chunk_id]["retrieval_type"] = "hybrid"
        else:
            chunk_data[chunk_id] = result

    sorted_chunks = sorted(
        rrf_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    fused_results = []

    for chunk_id, score in sorted_chunks:
        result = chunk_data[chunk_id].copy()
        result["rrf_score"] = float(score)
        fused_results.append(result)

    return fused_results


def hybrid_search(
    query: str,
    conversation_id: str,
    top_k: int = RETRIEVAL_TOP_K
) -> List[Dict]:
    """
    Perform hybrid search combining semantic and keyword search.
    """
    semantic_results = semantic_search(query, conversation_id, top_k)
    keyword_results = keyword_search(query, conversation_id, top_k)

    fused_results = reciprocal_rank_fusion(
        semantic_results,
        keyword_results
    )

    return fused_results[:top_k]