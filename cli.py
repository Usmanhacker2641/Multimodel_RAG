#!/usr/bin/env python3
"""
Command-line interface for MultiRAG system
"""

import argparse
import sys
import os
from multirag import MultiRAG


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="MultiRAG - Multi-Model Retrieval-Augmented Generation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Index documents
  python cli.py --load documents/

  # Query the system
  python cli.py --query "What is artificial intelligence?"

  # Query with custom config
  python cli.py --config custom_config.yaml --query "What is machine learning?"

  # Query with sources
  python cli.py --query "Explain RAG" --show-sources
        """
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--api-key',
        type=str,
        help='OpenAI API key (can also use OPENAI_API_KEY env var)'
    )
    
    parser.add_argument(
        '--load',
        type=str,
        metavar='PATH',
        help='Load and index documents from file or directory'
    )
    
    parser.add_argument(
        '--query',
        type=str,
        metavar='QUESTION',
        help='Query the RAG system'
    )
    
    parser.add_argument(
        '--show-sources',
        action='store_true',
        help='Show source documents with the answer'
    )
    
    parser.add_argument(
        '--sequential',
        action='store_true',
        help='Query models sequentially instead of in parallel'
    )
    
    parser.add_argument(
        '--load-existing',
        action='store_true',
        help='Load existing vector store instead of creating new one'
    )
    
    args = parser.parse_args()
    
    # Check for API key
    if args.api_key:
        os.environ['OPENAI_API_KEY'] = args.api_key
    elif 'OPENAI_API_KEY' not in os.environ:
        print("Warning: OPENAI_API_KEY not set. Set it via --api-key or environment variable.")
        if args.query:
            print("Error: API key required for querying. Exiting.")
            sys.exit(1)
    
    try:
        # Initialize MultiRAG
        print("Initializing MultiRAG system...")
        rag = MultiRAG(config_path=args.config)
        print("✓ System initialized\n")
        
        # Load documents if specified
        if args.load:
            print(f"Loading documents from: {args.load}")
            rag.load_documents(args.load)
            print("✓ Documents loaded and indexed\n")
        
        # Load existing vector store if specified
        elif args.load_existing:
            print("Loading existing vector store...")
            rag.load_existing_vector_store()
            print("✓ Vector store loaded\n")
        
        # Query if specified
        if args.query:
            if not args.load and not args.load_existing:
                print("Error: Must load documents (--load) or existing vector store (--load-existing) before querying")
                sys.exit(1)
            
            print(f"Question: {args.query}\n")
            print("=" * 70)
            
            # Query with or without sources
            if args.show_sources:
                result = rag.query_with_sources(args.query)
            else:
                result = rag.query(args.query, use_parallel=not args.sequential)
            
            print()
            
            # Display results
            if result.get('strategy') == 'all_responses':
                print("Responses from all models:\n")
                for resp in result['responses']:
                    print(f"{resp['model']}:")
                    print(f"  {resp['response']}\n")
            else:
                print("Answer:")
                print(f"  {result['response']}\n")
                
                print(f"Primary Model: {result.get('primary_model', 'N/A')}")
                print(f"Models Used: {', '.join(result['models_used'])}")
                print(f"Confidence: {result.get('confidence', 0):.2f}")
                
                # Show sources if requested
                if args.show_sources and 'formatted_sources' in result:
                    print("\n" + "=" * 70)
                    print("Source Documents:\n")
                    for source in result['formatted_sources']:
                        print(f"Source {source['source_id']}:")
                        print(f"  {source['content']}")
                        if source.get('metadata'):
                            print(f"  Metadata: {source['metadata']}")
                        print()
            
            print("=" * 70)
        
        # If neither load nor query specified, show help
        if not args.load and not args.query and not args.load_existing:
            parser.print_help()
            sys.exit(0)
    
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
