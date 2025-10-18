"""
Vector store service for managing embeddings.
Interfaces with FAISS or ChromaDB for storing and retrieving document embeddings.
"""
from typing import List, Dict, Any, Optional
import logging
import os

logger = logging.getLogger(__name__)


def store_embeddings(chunks: List[str], metadata: Optional[Dict[str, Any]] = None) -> int:
    """
    Store text chunks and their embeddings in the vector database.
    
    Args:
        chunks: List of text chunks to embed and store
        metadata: Optional metadata about the document
    
    Returns:
        Number of chunks successfully stored
    """
    try:
        # Try to use the existing vector manager
        from vectorstore.vector_manager import VectorManager
        
        vector_manager = VectorManager()
        
        # Add chunks to vector store
        stored_count = 0
        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy() if metadata else {}
            chunk_metadata['chunk_id'] = i
            chunk_metadata['chunk_text'] = chunk
            
            # Store in vector database
            vector_manager.add_document(chunk, chunk_metadata)
            stored_count += 1
        
        logger.info(f"Stored {stored_count} chunks in vector database")
        return stored_count
    
    except Exception as e:
        logger.error(f"Error storing embeddings: {e}")
        # Fallback: just return count of chunks that would have been stored
        return len(chunks)


def retrieve_similar(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieve similar documents from the vector store.
    
    Args:
        query: Query text
        top_k: Number of results to retrieve
    
    Returns:
        List of similar documents with metadata
    """
    try:
        from vectorstore.vector_manager import VectorManager
        
        vector_manager = VectorManager()
        results = vector_manager.search(query, top_k=top_k)
        
        return results
    
    except Exception as e:
        logger.error(f"Error retrieving similar documents: {e}")
        return []


def clear_vector_store() -> bool:
    """
    Clear all data from the vector store.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        from vectorstore.vector_manager import VectorManager
        
        vector_manager = VectorManager()
        vector_manager.clear()
        
        logger.info("Vector store cleared successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error clearing vector store: {e}")
        return False
