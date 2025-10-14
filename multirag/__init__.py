"""
MultiRAG - Multi-Model Retrieval-Augmented Generation System

A RAG system that uses multiple models in parallel to provide
high-accuracy answers through ensemble methods.
"""

__version__ = "0.1.0"

from .multi_rag import MultiRAG
from .document_processor import DocumentProcessor
from .vector_store_manager import VectorStoreManager
from .response_aggregator import ResponseAggregator

__all__ = [
    "MultiRAG",
    "DocumentProcessor",
    "VectorStoreManager",
    "ResponseAggregator",
]
