"""
Document Processing Module

Handles document loading, chunking, and preprocessing for RAG.
"""

from typing import List, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
import os


class DocumentProcessor:
    """Process and chunk documents for RAG system."""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """
        Initialize document processor.
        
        Args:
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
    
    def load_documents(self, file_path: str) -> List:
        """
        Load documents from file or directory.
        
        Args:
            file_path: Path to file or directory
            
        Returns:
            List of loaded documents
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Path not found: {file_path}")
        
        documents = []
        
        if os.path.isdir(file_path):
            # Load all text and PDF files from directory
            txt_loader = DirectoryLoader(
                file_path,
                glob="**/*.txt",
                loader_cls=TextLoader
            )
            pdf_loader = DirectoryLoader(
                file_path,
                glob="**/*.pdf",
                loader_cls=PyPDFLoader
            )
            documents.extend(txt_loader.load())
            documents.extend(pdf_loader.load())
        elif file_path.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
            documents = loader.load()
        elif file_path.endswith('.txt'):
            loader = TextLoader(file_path)
            documents = loader.load()
        else:
            raise ValueError(f"Unsupported file type: {file_path}")
        
        return documents
    
    def chunk_documents(self, documents: List) -> List:
        """
        Split documents into chunks.
        
        Args:
            documents: List of documents to chunk
            
        Returns:
            List of chunked documents
        """
        return self.text_splitter.split_documents(documents)
    
    def process_documents(self, file_path: str) -> List:
        """
        Load and chunk documents in one step.
        
        Args:
            file_path: Path to file or directory
            
        Returns:
            List of processed document chunks
        """
        documents = self.load_documents(file_path)
        return self.chunk_documents(documents)
    
    def process_text(self, text: str) -> List:
        """
        Process raw text into chunks.
        
        Args:
            text: Raw text to process
            
        Returns:
            List of text chunks
        """
        return self.text_splitter.split_text(text)
