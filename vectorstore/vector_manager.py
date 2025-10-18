import os
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import numpy as np

# Vector database imports
try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    logging.warning("ChromaDB not installed. Install with: pip install chromadb")

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logging.warning("FAISS not installed. Install with: pip install faiss-cpu")

try:
    import pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    logging.warning("Pinecone not installed. Install with: pip install pinecone-client")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorManager:
    """
    Manages vector database operations for document retrieval.
    Supports ChromaDB, FAISS, and Pinecone.
    """
    
    def __init__(
        self,
        db_type: str = "pinecone",
        persist_directory: str = "./data/vectorstore",
        collection_name: str = "documents",
        embedding_dimension: int = 384  # Default for all-MiniLM-L6-v2
    ):
        """
        Initialize the vector database manager.
        
        Args:
            db_type: Type of vector database ("chroma", "faiss", or "pinecone")
            persist_directory: Directory for persistent storage
            collection_name: Name of the collection/index
            embedding_dimension: Dimension of embedding vectors
        """
        self.db_type = db_type.lower()
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_dimension = embedding_dimension
        
        # Ensure directory exists
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize the appropriate database
        self.db = None
        self.collection = None
        self.index = None
        self.metadata_store = {}  # For FAISS metadata storage
        
        self._init_vectorstore()
        
    def _init_vectorstore(self):
        """Initialize or load the vector database."""
        if self.db_type == "chroma":
            self._init_chroma()
        elif self.db_type == "faiss":
            self._init_faiss()
        elif self.db_type == "pinecone":
            self._init_pinecone()
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
    
    def _init_chroma(self):
        """Initialize ChromaDB with persistent storage."""
        if not CHROMA_AVAILABLE:
            raise ImportError("ChromaDB not installed. Install with: pip install chromadb")
        
        try:
            # Initialize ChromaDB client with persistent storage
            self.db = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=self.persist_directory
            ))
            
            # Get or create collection
            self.collection = self.db.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}  # Use cosine similarity
            )
            
            logger.info(f"ChromaDB initialized. Collection: {self.collection_name}")
            logger.info(f"Current document count: {self.collection.count()}")
            
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            raise
    
    def _init_faiss(self):
        """Initialize FAISS index with disk persistence."""
        if not FAISS_AVAILABLE:
            raise ImportError("FAISS not installed. Install with: pip install faiss-cpu")
        
        index_path = os.path.join(self.persist_directory, f"{self.collection_name}.faiss")
        metadata_path = os.path.join(self.persist_directory, f"{self.collection_name}_metadata.json")
        
        try:
            # Try to load existing index
            if os.path.exists(index_path):
                self.index = faiss.read_index(index_path)
                logger.info(f"Loaded existing FAISS index from {index_path}")
                
                # Load metadata
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        self.metadata_store = json.load(f)
                    logger.info(f"Loaded {len(self.metadata_store)} metadata entries")
            else:
                # Create new index using Inner Product (for normalized vectors)
                self.index = faiss.IndexFlatIP(self.embedding_dimension)
                logger.info(f"Created new FAISS index with dimension {self.embedding_dimension}")
                
        except Exception as e:
            logger.error(f"Error initializing FAISS: {e}")
            raise
    
    def _init_pinecone(self):
        """Initialize Pinecone index."""
        if not PINECONE_AVAILABLE:
            raise ImportError("Pinecone not installed. Install with: pip install pinecone-client")
        
        try:
            api_key = "pcsk_6NJ1yP_274S7UJSDfxye3UwqxRr9ttKVnKbQunimMjkA3ms9QRkU6nL6nYWP1bRs1fsXtL"
            environment = "gcp-starter"
            
            if not api_key or not environment:
                raise ValueError("Pinecone API key and environment must be hardcoded.")

            pinecone.init(api_key=api_key, environment=environment)
            
            if self.collection_name not in pinecone.list_indexes():
                pinecone.create_index(
                    self.collection_name,
                    dimension=self.embedding_dimension,
                    metric='cosine'
                )
                logger.info(f"Created new Pinecone index: {self.collection_name}")
            
            self.index = pinecone.Index(self.collection_name)
            logger.info(f"Pinecone initialized. Index: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Error initializing Pinecone: {e}")
            raise
    
    def add_embeddings(
        self,
        documents: List[str],
        embeddings: np.ndarray,
        metadata: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add document embeddings to the vector database.
        
        Args:
            documents: List of document text chunks
            embeddings: Numpy array of embeddings (shape: [n_docs, embedding_dim])
            metadata: List of metadata dictionaries for each document
            ids: Optional list of document IDs
            
        Returns:
            List of document IDs
        """
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents and embeddings must match")
        
        # Generate IDs if not provided
        if ids is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ids = [f"doc_{timestamp}_{i}" for i in range(len(documents))]
        
        # Prepare metadata
        if metadata is None:
            metadata = [{"timestamp": datetime.now().isoformat()} for _ in documents]
        else:
            # Ensure all metadata has timestamp
            for meta in metadata:
                if "timestamp" not in meta:
                    meta["timestamp"] = datetime.now().isoformat()
        
        if self.db_type == "chroma":
            return self._add_to_chroma(documents, embeddings, metadata, ids)
        elif self.db_type == "faiss":
            return self._add_to_faiss(documents, embeddings, metadata, ids)
        elif self.db_type == "pinecone":
            return self._add_to_pinecone(documents, embeddings, metadata, ids)
    
    def _add_to_chroma(
        self,
        documents: List[str],
        embeddings: np.ndarray,
        metadata: List[Dict[str, Any]],
        ids: List[str]
    ) -> List[str]:
        """Add embeddings to ChromaDB."""
        try:
            self.collection.add(
                embeddings=embeddings.tolist(),
                documents=documents,
                metadatas=metadata,
                ids=ids
            )
            logger.info(f"Added {len(documents)} documents to ChromaDB")
            return ids
            
        except Exception as e:
            logger.error(f"Error adding to ChromaDB: {e}")
            raise
    
    def _add_to_faiss(
        self,
        documents: List[str],
        embeddings: np.ndarray,
        metadata: List[Dict[str, Any]],
        ids: List[str]
    ) -> List[str]:
        """Add embeddings to FAISS index."""
        try:
            # Normalize embeddings for cosine similarity
            normalized_embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
            
            # Get current index for new IDs
            start_idx = self.index.ntotal
            
            # Add to FAISS index
            self.index.add(normalized_embeddings.astype('float32'))
            
            # Store metadata with mapping to FAISS indices
            for i, (doc_id, doc, meta) in enumerate(zip(ids, documents, metadata)):
                faiss_idx = start_idx + i
                self.metadata_store[str(faiss_idx)] = {
                    "id": doc_id,
                    "document": doc,
                    "metadata": meta
                }
            
            # Persist to disk
            self._save_faiss()
            
            logger.info(f"Added {len(documents)} documents to FAISS")
            return ids
            
        except Exception as e:
            logger.error(f"Error adding to FAISS: {e}")
            raise
    
    def _add_to_pinecone(
        self,
        documents: List[str],
        embeddings: np.ndarray,
        metadata: List[Dict[str, Any]],
        ids: List[str]
    ) -> List[str]:
        """Add embeddings to Pinecone."""
        try:
            vectors_to_upsert = []
            for i, (doc_id, embedding) in enumerate(zip(ids, embeddings)):
                meta = metadata[i]
                meta['document'] = documents[i]
                vectors_to_upsert.append((doc_id, embedding.tolist(), meta))

            self.index.upsert(vectors=vectors_to_upsert)
            logger.info(f"Added {len(documents)} documents to Pinecone")
            return ids
            
        except Exception as e:
            logger.error(f"Error adding to Pinecone: {e}")
            raise

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[str], List[Dict[str, Any]], List[float]]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filter_metadata: Optional metadata filters (ChromaDB only)
            
        Returns:
            Tuple of (documents, metadata, distances)
        """
        if self.db_type == "chroma":
            return self._search_chroma(query_embedding, top_k, filter_metadata)
        elif self.db_type == "faiss":
            return self._search_faiss(query_embedding, top_k)
        elif self.db_type == "pinecone":
            return self._search_pinecone(query_embedding, top_k, filter_metadata)

    def _search_chroma(
        self,
        query_embedding: np.ndarray,
        top_k: int,
        filter_metadata: Optional[Dict[str, Any]]
    ) -> Tuple[List[str], List[Dict[str, Any]], List[float]]:
        """Search ChromaDB collection."""
        try:
            # Prepare query
            query_params = {
                "query_embeddings": [query_embedding.tolist()],
                "n_results": top_k
            }
            
            # Add metadata filter if provided
            if filter_metadata:
                query_params["where"] = filter_metadata
            
            results = self.collection.query(**query_params)
            
            documents = results['documents'][0] if results['documents'] else []
            metadata = results['metadatas'][0] if results['metadatas'] else []
            distances = results['distances'][0] if results['distances'] else []
            
            logger.info(f"ChromaDB search returned {len(documents)} results")
            return documents, metadata, distances
            
        except Exception as e:
            logger.error(f"Error searching ChromaDB: {e}")
            raise
    
    def _search_faiss(
        self,
        query_embedding: np.ndarray,
        top_k: int
    ) -> Tuple[List[str], List[Dict[str, Any]], List[float]]:
        """Search FAISS index."""
        try:
            # Normalize query embedding
            normalized_query = query_embedding / np.linalg.norm(query_embedding)
            normalized_query = normalized_query.reshape(1, -1).astype('float32')
            
            # Search
            distances, indices = self.index.search(normalized_query, top_k)
            
            # Retrieve metadata
            documents = []
            metadata = []
            scores = []
            
            for idx, dist in zip(indices[0], distances[0]):
                if idx != -1 and str(idx) in self.metadata_store:
                    entry = self.metadata_store[str(idx)]
                    documents.append(entry['document'])
                    metadata.append(entry['metadata'])
                    scores.append(float(dist))
            
            logger.info(f"FAISS search returned {len(documents)} results")
            return documents, metadata, scores
            
        except Exception as e:
            logger.error(f"Error searching FAISS: {e}")
            raise
    
    def _search_pinecone(
        self,
        query_embedding: np.ndarray,
        top_k: int,
        filter_metadata: Optional[Dict[str, Any]]
    ) -> Tuple[List[str], List[Dict[str, Any]], List[float]]:
        """Search Pinecone index."""
        try:
            results = self.index.query(
                vector=query_embedding.tolist(),
                top_k=top_k,
                include_metadata=True,
                filter=filter_metadata
            )
            
            documents = [res['metadata'].pop('document', '') for res in results['matches']]
            metadata = [res['metadata'] for res in results['matches']]
            scores = [res['score'] for res in results['matches']]
            
            logger.info(f"Pinecone search returned {len(documents)} results")
            return documents, metadata, scores
            
        except Exception as e:
            logger.error(f"Error searching Pinecone: {e}")
            raise

    def delete_embeddings(self, ids: Optional[List[str]] = None, filter_metadata: Optional[Dict[str, Any]] = None):
        """
        Delete embeddings by IDs or metadata filter.
        
        Args:
            ids: List of document IDs to delete
            filter_metadata: Metadata filter for deletion (ChromaDB only)
        """
        if self.db_type == "chroma":
            self._delete_from_chroma(ids, filter_metadata)
        elif self.db_type == "faiss":
            self._delete_from_faiss(ids)
        elif self.db_type == "pinecone":
            self._delete_from_pinecone(ids, filter_metadata)

    def _delete_from_chroma(self, ids: Optional[List[str]], filter_metadata: Optional[Dict[str, Any]]):
        """Delete from ChromaDB."""
        try:
            if ids:
                self.collection.delete(ids=ids)
                logger.info(f"Deleted {len(ids)} documents from ChromaDB")
            elif filter_metadata:
                self.collection.delete(where=filter_metadata)
                logger.info(f"Deleted documents matching filter from ChromaDB")
            else:
                logger.warning("No deletion criteria provided")
                
        except Exception as e:
            logger.error(f"Error deleting from ChromaDB: {e}")
            raise
    
    def _delete_from_faiss(self, ids: Optional[List[str]]):
        """Delete from FAISS (requires rebuilding index)."""
        if not ids:
            logger.warning("No IDs provided for FAISS deletion")
            return
        
        try:
            # FAISS doesn't support direct deletion, so we rebuild
            ids_to_delete = set(ids)
            new_metadata = {}
            vectors_to_keep = []
            
            for idx_str, entry in self.metadata_store.items():
                if entry['id'] not in ids_to_delete:
                    new_metadata[str(len(vectors_to_keep))] = entry
                    # Note: This requires re-adding all vectors (limitation of FAISS)
                    # In production, consider using FAISS with IDMap for better deletion support
            
            logger.warning("FAISS deletion requires full index rebuild. Consider using ChromaDB for frequent deletions.")
            self.metadata_store = new_metadata
            self._save_faiss()
            
        except Exception as e:
            logger.error(f"Error deleting from FAISS: {e}")
            raise
    
    def _delete_from_pinecone(self, ids: Optional[List[str]], filter_metadata: Optional[Dict[str, Any]]):
        """Delete from Pinecone."""
        try:
            if ids:
                self.index.delete(ids=ids)
                logger.info(f"Deleted {len(ids)} documents from Pinecone")
            elif filter_metadata:
                self.index.delete(filter=filter_metadata)
                logger.info(f"Deleted documents matching filter from Pinecone")
            else:
                logger.warning("No deletion criteria provided")
                
        except Exception as e:
            logger.error(f"Error deleting from Pinecone: {e}")
            raise

    def update_embedding(self, chunk_id: str, new_embedding: np.ndarray, new_metadata: Optional[Dict[str, Any]] = None):
        """
        Update an existing embedding.
        
        Args:
            chunk_id: ID of the chunk to update
            new_embedding: New embedding vector
            new_metadata: Optional new metadata
        """
        # Delete old and add new (simple approach)
        self.delete_embeddings(ids=[chunk_id])
        
        if new_metadata:
            self.add_embeddings(
                documents=[new_metadata.get('document', '')],
                embeddings=new_embedding.reshape(1, -1),
                metadata=[new_metadata],
                ids=[chunk_id]
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector database.
        
        Returns:
            Dictionary with database statistics
        """
        if self.db_type == "chroma":
            return self._get_chroma_stats()
        elif self.db_type == "faiss":
            return self._get_faiss_stats()
        elif self.db_type == "pinecone":
            return self._get_pinecone_stats()

    def _get_chroma_stats(self) -> Dict[str, Any]:
        """Get ChromaDB statistics."""
        try:
            count = self.collection.count()
            
            # Get sample to analyze categories
            sample = self.collection.peek(limit=min(100, count))
            categories = set()
            file_types = set()
            
            for meta in sample.get('metadatas', []):
                if 'category' in meta:
                    categories.add(meta['category'])
                if 'file_type' in meta:
                    file_types.add(meta['file_type'])
            
            return {
                "database_type": "ChromaDB",
                "total_documents": count,
                "collection_name": self.collection_name,
                "categories": list(categories),
                "file_types": list(file_types),
                "persist_directory": self.persist_directory
            }
            
        except Exception as e:
            logger.error(f"Error getting ChromaDB stats: {e}")
            return {"error": str(e)}
    
    def _get_faiss_stats(self) -> Dict[str, Any]:
        """Get FAISS statistics."""
        try:
            categories = set()
            file_types = set()
            
            for entry in self.metadata_store.values():
                meta = entry.get('metadata', {})
                if 'category' in meta:
                    categories.add(meta['category'])
                if 'file_type' in meta:
                    file_types.add(meta['file_type'])
            
            return {
                "database_type": "FAISS",
                "total_documents": self.index.ntotal,
                "embedding_dimension": self.embedding_dimension,
                "categories": list(categories),
                "file_types": list(file_types),
                "persist_directory": self.persist_directory
            }
            
        except Exception as e:
            logger.error(f"Error getting FAISS stats: {e}")
            return {"error": str(e)}
    
    def _get_pinecone_stats(self) -> Dict[str, Any]:
        """Get Pinecone statistics."""
        try:
            stats = self.index.describe_index_stats()
            return {
                "database_type": "Pinecone",
                "total_documents": stats['total_vector_count'],
                "embedding_dimension": stats['dimension'],
                "index_name": self.collection_name,
            }
        except Exception as e:
            logger.error(f"Error getting Pinecone stats: {e}")
            return {"error": str(e)}

    def _save_faiss(self):
        """Save FAISS index and metadata to disk."""
        try:
            index_path = os.path.join(self.persist_directory, f"{self.collection_name}.faiss")
            metadata_path = os.path.join(self.persist_directory, f"{self.collection_name}_metadata.json")
            
            faiss.write_index(self.index, index_path)
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata_store, f, ensure_ascii=False, indent=2)
            
            logger.info("FAISS index and metadata saved to disk")
            
        except Exception as e:
            logger.error(f"Error saving FAISS: {e}")
            raise
    
    def clear_all(self):
        """Clear all data from the vector database."""
        if self.db_type == "chroma":
            self.db.delete_collection(self.collection_name)
            self.collection = self.db.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("ChromaDB collection cleared")
        else:
            self.index = faiss.IndexFlatIP(self.embedding_dimension)
            self.metadata_store = {}
            self._save_faiss()
            logger.info("FAISS index cleared")
        if self.db_type == "pinecone":
            self.index.delete(delete_all=True)
            logger.info("Pinecone index cleared")


# Example usage
if __name__ == "__main__":
    # Initialize with ChromaDB
    vm = VectorManager(db_type="chroma", persist_directory="./data/vectorstore")
    
    # Example embeddings (384-dimensional for all-MiniLM-L6-v2)
    sample_embeddings = np.random.rand(3, 384)
    sample_docs = [
        "This is a sample document about AI.",
        "Machine learning is a subset of AI.",
        "Natural language processing enables text understanding."
    ]
    sample_metadata = [
        {"file_type": "pdf", "category": "tech", "source": "document1.pdf"},
        {"file_type": "url", "category": "tech", "source": "https://example.com"},
        {"file_type": "audio", "category": "science", "source": "lecture.mp3"}
    ]
    
    # Add documents
    doc_ids = vm.add_embeddings(sample_docs, sample_embeddings, sample_metadata)
    print(f"Added documents: {doc_ids}")
    
    # Search
    query_embedding = np.random.rand(384)
    docs, meta, scores = vm.search(query_embedding, top_k=2)
    print(f"Search results: {len(docs)} documents found")
    
    # Get stats
    stats = vm.get_stats()
    print(f"Database stats: {stats}")