"""
Vector Store Manager Module

Manages vector stores for document retrieval.
"""

from typing import List, Optional
from langchain_community.vectorstores import Chroma, FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document


class VectorStoreManager:
    """Manage vector stores for document retrieval."""
    
    def __init__(
        self,
        store_type: str = "chroma",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        collection_name: str = "multirag_collection",
        persist_directory: Optional[str] = None
    ):
        """
        Initialize vector store manager.
        
        Args:
            store_type: Type of vector store ('chroma' or 'faiss')
            embedding_model: Name of embedding model to use
            collection_name: Name of the collection
            persist_directory: Directory to persist vector store
        """
        self.store_type = store_type.lower()
        self.collection_name = collection_name
        self.persist_directory = persist_directory or f"./{store_type}_db"
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'}
        )
        
        self.vector_store = None
    
    def create_vector_store(self, documents: List[Document]) -> None:
        """
        Create vector store from documents.
        
        Args:
            documents: List of documents to index
        """
        if not documents:
            raise ValueError("No documents provided")
        
        if self.store_type == "chroma":
            self.vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                collection_name=self.collection_name,
                persist_directory=self.persist_directory
            )
        elif self.store_type == "faiss":
            self.vector_store = FAISS.from_documents(
                documents=documents,
                embedding=self.embeddings
            )
            # Save FAISS index
            self.vector_store.save_local(self.persist_directory)
        else:
            raise ValueError(f"Unsupported vector store type: {self.store_type}")
    
    def load_vector_store(self) -> None:
        """Load existing vector store from disk."""
        if self.store_type == "chroma":
            self.vector_store = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory
            )
        elif self.store_type == "faiss":
            self.vector_store = FAISS.load_local(
                self.persist_directory,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
        else:
            raise ValueError(f"Unsupported vector store type: {self.store_type}")
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to existing vector store.
        
        Args:
            documents: List of documents to add
        """
        if self.vector_store is None:
            raise ValueError("Vector store not initialized. Call create_vector_store or load_vector_store first.")
        
        self.vector_store.add_documents(documents)
        
        # Persist changes
        if self.store_type == "faiss":
            self.vector_store.save_local(self.persist_directory)
    
    def similarity_search(
        self,
        query: str,
        k: int = 5,
        score_threshold: Optional[float] = None
    ) -> List[Document]:
        """
        Search for similar documents.
        
        Args:
            query: Query text
            k: Number of documents to retrieve
            score_threshold: Minimum similarity score threshold
            
        Returns:
            List of relevant documents
        """
        if self.vector_store is None:
            raise ValueError("Vector store not initialized")
        
        if score_threshold is not None:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            # Filter by score threshold
            filtered_results = [doc for doc, score in results if score >= score_threshold]
            return filtered_results
        else:
            return self.vector_store.similarity_search(query, k=k)
    
    def as_retriever(self, k: int = 5):
        """
        Get vector store as a retriever.
        
        Args:
            k: Number of documents to retrieve
            
        Returns:
            Retriever object
        """
        if self.vector_store is None:
            raise ValueError("Vector store not initialized")
        
        return self.vector_store.as_retriever(search_kwargs={"k": k})
