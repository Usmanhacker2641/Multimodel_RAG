"""
Multi-Model RAG System

Main orchestrator for parallel multi-model RAG queries.
"""

from typing import List, Dict, Optional, Callable
import concurrent.futures
import os
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import yaml

from .document_processor import DocumentProcessor
from .vector_store_manager import VectorStoreManager
from .response_aggregator import ResponseAggregator


class MultiRAG:
    """Multi-Model Retrieval-Augmented Generation System."""
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize MultiRAG system.
        
        Args:
            config_path: Path to configuration file
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
        """
        # Load configuration
        if config_path:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = self._default_config()
        
        # Set API key
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
        elif 'OPENAI_API_KEY' not in os.environ:
            print("Warning: OPENAI_API_KEY not set. Set it via environment variable or api_key parameter.")
        
        # Initialize components
        self.document_processor = DocumentProcessor(
            chunk_size=self.config['vector_store']['chunk_size'],
            chunk_overlap=self.config['vector_store']['chunk_overlap']
        )
        
        self.vector_store_manager = VectorStoreManager(
            store_type=self.config['vector_store']['type'],
            embedding_model=self.config['vector_store']['embedding_model'],
            collection_name=self.config['vector_store']['collection_name']
        )
        
        self.response_aggregator = ResponseAggregator(
            strategy=self.config['aggregation']['strategy'],
            weights=self.config['aggregation']['weights']
        )
        
        # Initialize models
        self.models = self._initialize_models()
        
        # QA chains
        self.qa_chains = {}
    
    def _default_config(self) -> Dict:
        """Return default configuration."""
        return {
            'models': [
                {
                    'name': 'gpt-3.5-turbo',
                    'provider': 'openai',
                    'temperature': 0.7,
                    'max_tokens': 500,
                    'enabled': True
                }
            ],
            'vector_store': {
                'type': 'chroma',
                'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2',
                'chunk_size': 1000,
                'chunk_overlap': 200,
                'collection_name': 'multirag_collection'
            },
            'retrieval': {
                'top_k': 5,
                'score_threshold': 0.5
            },
            'aggregation': {
                'strategy': 'weighted_voting',
                'weights': {'gpt-3.5-turbo': 1.0}
            }
        }
    
    def _initialize_models(self) -> Dict[str, ChatOpenAI]:
        """Initialize LLM models from config."""
        models = {}
        
        for model_config in self.config['models']:
            if not model_config.get('enabled', True):
                continue
            
            model_name = model_config['name']
            
            if model_config['provider'] == 'openai':
                models[model_name] = ChatOpenAI(
                    model=model_name,
                    temperature=model_config.get('temperature', 0.7),
                    max_tokens=model_config.get('max_tokens', 500)
                )
        
        return models
    
    def load_documents(self, file_path: str) -> None:
        """
        Load and index documents.
        
        Args:
            file_path: Path to document(s) to load
        """
        print(f"Loading documents from {file_path}...")
        documents = self.document_processor.process_documents(file_path)
        print(f"Processed {len(documents)} document chunks")
        
        print("Creating vector store...")
        self.vector_store_manager.create_vector_store(documents)
        print("Vector store created successfully")
        
        self._create_qa_chains()
    
    def load_existing_vector_store(self) -> None:
        """Load existing vector store from disk."""
        print("Loading existing vector store...")
        self.vector_store_manager.load_vector_store()
        print("Vector store loaded successfully")
        
        self._create_qa_chains()
    
    def _create_qa_chains(self) -> None:
        """Create QA chains for each model."""
        retriever = self.vector_store_manager.as_retriever(
            k=self.config['retrieval']['top_k']
        )
        
        # Custom prompt template
        template = """Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Use three sentences maximum and keep the answer concise.

Context: {context}

Question: {question}

Answer:"""
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        for model_name, model in self.models.items():
            self.qa_chains[model_name] = RetrievalQA.from_chain_type(
                llm=model,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True,
                chain_type_kwargs={"prompt": prompt}
            )
    
    def _query_single_model(
        self,
        model_name: str,
        query: str
    ) -> Dict:
        """
        Query a single model.
        
        Args:
            model_name: Name of the model
            query: Query string
            
        Returns:
            Response dictionary
        """
        try:
            qa_chain = self.qa_chains[model_name]
            result = qa_chain.invoke({"query": query})
            
            return {
                'model': model_name,
                'response': result['result'],
                'sources': result.get('source_documents', []),
                'score': 0.8  # Default score, could be improved with actual scoring
            }
        except Exception as e:
            print(f"Error querying {model_name}: {str(e)}")
            return {
                'model': model_name,
                'response': f"Error: {str(e)}",
                'sources': [],
                'score': 0.0
            }
    
    def query(
        self,
        question: str,
        use_parallel: bool = True
    ) -> Dict:
        """
        Query all enabled models and aggregate responses.
        
        Args:
            question: Question to ask
            use_parallel: Whether to query models in parallel
            
        Returns:
            Aggregated response dictionary
        """
        if not self.qa_chains:
            raise ValueError("No QA chains initialized. Call load_documents or load_existing_vector_store first.")
        
        print(f"\nQuerying {len(self.models)} models...")
        
        responses = []
        
        if use_parallel:
            # Query models in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.models)) as executor:
                future_to_model = {
                    executor.submit(self._query_single_model, model_name, question): model_name
                    for model_name in self.models.keys()
                }
                
                for future in concurrent.futures.as_completed(future_to_model):
                    model_name = future_to_model[future]
                    try:
                        response = future.result()
                        responses.append(response)
                        print(f"✓ {model_name} responded")
                    except Exception as e:
                        print(f"✗ {model_name} failed: {str(e)}")
        else:
            # Query models sequentially
            for model_name in self.models.keys():
                response = self._query_single_model(model_name, question)
                responses.append(response)
                print(f"✓ {model_name} responded")
        
        # Aggregate responses
        print("\nAggregating responses...")
        aggregated = self.response_aggregator.aggregate(responses)
        
        # Add confidence score
        aggregated['confidence'] = self.response_aggregator.calculate_confidence(responses)
        
        return aggregated
    
    def query_with_sources(self, question: str) -> Dict:
        """
        Query and return response with source documents.
        
        Args:
            question: Question to ask
            
        Returns:
            Response with sources
        """
        result = self.query(question)
        
        # Format sources
        if 'sources' in result and result['sources']:
            formatted_sources = []
            for i, doc in enumerate(result['sources'][:3]):  # Top 3 sources
                formatted_sources.append({
                    'source_id': i + 1,
                    'content': doc.page_content[:200] + '...',
                    'metadata': doc.metadata
                })
            result['formatted_sources'] = formatted_sources
        
        return result
