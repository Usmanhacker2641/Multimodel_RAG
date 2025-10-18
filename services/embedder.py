from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextEmbedder:
    """
    Text Embedding Generator using SentenceTransformers
    Converts text chunks into vector embeddings for semantic search
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding model
        
        Args:
            model_name: Name of the SentenceTransformer model to use
        """
        try:
            logger.info(f"Loading embedding model: {model_name}")
            self.model = SentenceTransformer(model_name)
            self.model_name = model_name
            self.embedding_dimension = self.model.get_sentence_embedding_dimension()
            logger.info(f"Model loaded successfully. Embedding dimension: {self.embedding_dimension}")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def get_embeddings(self, chunks: Union[List[str], str], show_progress: bool = True) -> np.ndarray:
        """
        Generate embeddings for text chunks
        
        Args:
            chunks: Single text string or list of text chunks
            show_progress: Whether to show progress bar
            
        Returns:
            numpy array of embeddings
        """
        try:
            # Handle single string input
            if isinstance(chunks, str):
                chunks = [chunks]
            
            if not chunks:
                logger.warning("Empty chunks list provided")
                return np.array([])
            
            logger.info(f"Generating embeddings for {len(chunks)} chunks")
            embeddings = self.model.encode(
                chunks,
                show_progress_bar=show_progress,
                convert_to_numpy=True,
                normalize_embeddings=True
            )
            
            logger.info(f"Embeddings generated successfully. Shape: {embeddings.shape}")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors
        
        Returns:
            Integer dimension of embeddings
        """
        return self.embedding_dimension
    
    def encode_query(self, query: str) -> np.ndarray:
        """
        Encode a single query string
        
        Args:
            query: Query text to encode
            
        Returns:
            numpy array of the query embedding
        """
        try:
            logger.info(f"Encoding query: {query[:50]}...")
            embedding = self.model.encode(
                query,
                convert_to_numpy=True,
                normalize_embeddings=True
            )
            return embedding
        except Exception as e:
            logger.error(f"Error encoding query: {str(e)}")
            raise


# Initialize global embedder instance
embedder = TextEmbedder()


def get_embeddings(chunks: Union[List[str], str], show_progress: bool = True) -> np.ndarray:
    """
    Convenience function to generate embeddings
    
    Args:
        chunks: Single text string or list of text chunks
        show_progress: Whether to show progress bar
        
    Returns:
        numpy array of embeddings
    """
    return embedder.get_embeddings(chunks, show_progress)


class Embedder:
    """Thin wrapper around TextEmbedder for compatibility with pipeline code."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        global embedder
        if model_name != getattr(embedder, "model_name", model_name):
            # Re-initialize global embedder if a different model is requested
            embedder = TextEmbedder(model_name)
        self._embedder = embedder

    def embed(self, chunks: Union[List[str], str]) -> np.ndarray:
        return self._embedder.get_embeddings(chunks, show_progress=False)

    def embed_query(self, query: str) -> np.ndarray:
        return self._embedder.encode_query(query)


if __name__ == "__main__":
    # Test the embedder
    test_chunks = [
        "This is a sample text for embedding.",
        "Another example chunk to convert to vectors.",
        "Machine learning models convert text to numerical representations."
    ]
    
    logger.info("Testing embedder...")
    embeddings = get_embeddings(test_chunks)
    logger.info(f"Test successful! Generated {len(embeddings)} embeddings of dimension {embeddings.shape[1]}")