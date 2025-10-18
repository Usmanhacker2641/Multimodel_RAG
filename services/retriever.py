from typing import List, Dict, Any

from services.embedder import Embedder
from vectorstore.vector_manager import VectorManager


class Retriever:
    """Vector-store backed retriever that leverages the shared vector manager."""

    def __init__(self, vector_manager: VectorManager = None, embedder: Embedder = None):
        self.vector_manager = vector_manager or VectorManager()
        self.embedder = embedder or Embedder()

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        query_embedding = self.embedder.embed_query(query)
        documents, metadata, scores = self.vector_manager.search(query_embedding, top_k=top_k)
        results: List[Dict[str, Any]] = []
        for doc, meta, score in zip(documents, metadata, scores):
            results.append({
                "text": doc,
                "metadata": meta or {},
                "score": score
            })
        return results

    def get_context_text(self, query: str, top_k: int = 5) -> str:
        chunks = self.retrieve(query, top_k=top_k)
        return "\n\n".join(chunk.get("text", "") for chunk in chunks)