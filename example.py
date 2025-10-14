"""
Example usage of MultiRAG system

This script demonstrates how to use the MultiRAG system to:
1. Load documents
2. Create a vector store
3. Query multiple models in parallel
4. Get aggregated responses
"""

import os
from multirag import MultiRAG


def main():
    """Main example function."""
    
    # Initialize MultiRAG system
    # Option 1: Use config file
    rag = MultiRAG(config_path="config.yaml")
    
    # Option 2: Use default config with API key
    # rag = MultiRAG(api_key="your-openai-api-key")
    
    # Option 3: Set API key via environment variable
    # os.environ['OPENAI_API_KEY'] = 'your-api-key'
    # rag = MultiRAG()
    
    # Example 1: Load documents from a file
    print("=" * 60)
    print("Example 1: Loading documents")
    print("=" * 60)
    
    # Create a sample document for testing
    sample_doc_path = "sample_document.txt"
    with open(sample_doc_path, 'w') as f:
        f.write("""
        Artificial Intelligence and Machine Learning
        
        Artificial Intelligence (AI) is the simulation of human intelligence by machines.
        Machine Learning (ML) is a subset of AI that enables systems to learn from data.
        
        Deep Learning is a subset of ML that uses neural networks with multiple layers.
        Natural Language Processing (NLP) helps machines understand human language.
        
        Computer Vision enables machines to interpret visual information from the world.
        Reinforcement Learning teaches agents to make decisions through trial and error.
        
        RAG (Retrieval-Augmented Generation) combines retrieval and generation for better AI responses.
        Vector databases store embeddings for efficient similarity search.
        """)
    
    # Load and index documents
    rag.load_documents(sample_doc_path)
    
    # Example 2: Query the system
    print("\n" + "=" * 60)
    print("Example 2: Querying the system")
    print("=" * 60)
    
    questions = [
        "What is Artificial Intelligence?",
        "What is the difference between ML and Deep Learning?",
        "What is RAG?",
    ]
    
    for question in questions:
        print(f"\nQuestion: {question}")
        print("-" * 60)
        
        result = rag.query(question, use_parallel=True)
        
        # Display results based on aggregation strategy
        if result.get('strategy') == 'all_responses':
            print("\nResponses from all models:")
            for resp in result['responses']:
                print(f"\n{resp['model']}:")
                print(f"  {resp['response']}")
        else:
            print(f"\nAggregated Response:")
            print(f"  {result['response']}")
            print(f"\nPrimary Model: {result.get('primary_model', 'N/A')}")
            print(f"Models Used: {', '.join(result['models_used'])}")
            print(f"Confidence: {result.get('confidence', 0):.2f}")
    
    # Example 3: Query with sources
    print("\n" + "=" * 60)
    print("Example 3: Query with source documents")
    print("=" * 60)
    
    question = "What is Reinforcement Learning?"
    print(f"\nQuestion: {question}")
    print("-" * 60)
    
    result = rag.query_with_sources(question)
    
    print(f"\nResponse: {result['response']}")
    
    if 'formatted_sources' in result:
        print("\nSource Documents:")
        for source in result['formatted_sources']:
            print(f"\nSource {source['source_id']}:")
            print(f"  {source['content']}")
    
    # Example 4: Load existing vector store
    print("\n" + "=" * 60)
    print("Example 4: Loading existing vector store")
    print("=" * 60)
    
    # Create a new instance and load existing vector store
    rag2 = MultiRAG(config_path="config.yaml")
    rag2.load_existing_vector_store()
    
    result = rag2.query("What is NLP?")
    print(f"\nResponse: {result['response']}")
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
