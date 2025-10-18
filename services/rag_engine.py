"""RAG retrieval shim expected by backend routes.
Provides retrieve_context(question, top_k) -> list of chunks (dicts).
"""
try:
    from .retriever import Retriever
except Exception:
    Retriever = None


def retrieve_context(question: str, top_k: int = 5):
    """Retrieve top-k context chunks for the given question.

    If a Retriever implementation exists and has a built index, use it.
    Otherwise return an empty list.
    """
    try:
        if Retriever:
            # In this shim we assume someone has built a global retriever instance.
            # For now, create a temporary retriever without index and return empty.
            r = Retriever()
            return r.get_context_text(question, top_k=top_k)
    except Exception:
        pass

    return []
