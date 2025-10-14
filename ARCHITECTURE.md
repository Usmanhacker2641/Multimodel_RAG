# MultiRAG Architecture Documentation

## System Overview

MultiRAG is a multi-model Retrieval-Augmented Generation system that combines the power of multiple language models to provide high-accuracy answers through parallel processing and intelligent response aggregation.

## Core Components

### 1. Document Processor (`document_processor.py`)
Responsible for loading and preprocessing documents.

**Features:**
- Supports multiple document formats (PDF, TXT)
- Recursive text splitting with configurable chunk size and overlap
- Directory-based batch processing
- Raw text processing

**Key Methods:**
- `load_documents(file_path)`: Load documents from file or directory
- `chunk_documents(documents)`: Split documents into chunks
- `process_documents(file_path)`: One-step load and chunk
- `process_text(text)`: Process raw text into chunks

### 2. Vector Store Manager (`vector_store_manager.py`)
Manages vector databases for efficient document retrieval.

**Supported Vector Stores:**
- Chroma (default)
- FAISS

**Features:**
- Automatic embedding generation using HuggingFace models
- Persistent storage
- Similarity search with configurable parameters
- Score-based filtering

**Key Methods:**
- `create_vector_store(documents)`: Create new vector store
- `load_vector_store()`: Load existing vector store
- `similarity_search(query, k, score_threshold)`: Search for relevant documents
- `as_retriever(k)`: Get retriever interface

### 3. Response Aggregator (`response_aggregator.py`)
Intelligently combines responses from multiple models.

**Aggregation Strategies:**

#### Weighted Voting
- Assigns weights to different models
- Selects response with highest weighted score
- Best for when you trust certain models more

#### Majority Vote
- Selects most common response
- Democratic approach
- Best for binary or categorical answers

#### Best Score
- Selects response with highest confidence
- Quality over consensus
- Best for single best answer

#### All Responses
- Returns all model responses
- Useful for comparison and analysis
- Best for debugging or research

**Key Methods:**
- `aggregate(responses)`: Aggregate multiple responses
- `calculate_confidence(responses)`: Calculate overall confidence score

### 4. MultiRAG (`multi_rag.py`)
Main orchestrator that brings all components together.

**Features:**
- Parallel model querying using ThreadPoolExecutor
- Automatic QA chain creation for each model
- Configuration-based initialization
- Support for both OpenAI and custom models

**Key Methods:**
- `load_documents(file_path)`: Load and index documents
- `load_existing_vector_store()`: Load pre-existing vector store
- `query(question, use_parallel)`: Query all models
- `query_with_sources(question)`: Query with source document information

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Document Ingestion                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Documents (PDF/TXT) ──> Document Processor ──> Chunks      │
│                                      │                        │
│                                      v                        │
│                          HuggingFace Embeddings              │
│                                      │                        │
│                                      v                        │
│                          Vector Store (Chroma/FAISS)         │
│                                                               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                       Query Processing                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  User Query ──> Vector Store ──> Retrieved Documents        │
│                                                               │
│                      │                                        │
│                      v                                        │
│              ┌───────────────────┐                          │
│              │  Parallel Queries │                          │
│              ├───────────────────┤                          │
│              │                   │                          │
│     ┌────────┴────────┐    ┌────┴────────┐                │
│     │   Model 1       │    │   Model 2   │    ...          │
│     │  (GPT-3.5)      │    │   (GPT-4)   │                │
│     └────────┬────────┘    └────┬────────┘                │
│              │                   │                          │
│              └────────┬──────────┘                          │
│                       v                                      │
│              Response Aggregator                            │
│                       │                                      │
│                       v                                      │
│              Aggregated Result                              │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Configuration Schema

```yaml
models:
  - name: string              # Model identifier
    provider: string          # Provider (e.g., "openai")
    temperature: float        # Response randomness (0.0-1.0)
    max_tokens: int          # Maximum response length
    enabled: boolean         # Enable/disable model

vector_store:
  type: string               # "chroma" or "faiss"
  embedding_model: string    # HuggingFace model name
  chunk_size: int           # Text chunk size
  chunk_overlap: int        # Overlap between chunks
  collection_name: string   # Vector store collection name

retrieval:
  top_k: int                # Number of documents to retrieve
  score_threshold: float    # Minimum similarity score

aggregation:
  strategy: string          # Aggregation strategy
  weights: dict            # Model weights for weighted voting
```

## Performance Considerations

### Parallel Processing
- Uses ThreadPoolExecutor for concurrent model queries
- Speedup factor: ~N (where N = number of models)
- Example: 3 models → 3x faster than sequential

### Memory Usage
- Vector stores are loaded in memory
- Consider using FAISS for large document collections
- Embedding models run on CPU by default

### API Costs
- Each query calls multiple models
- Cost multiplier = number of enabled models
- Use model weights to prioritize cheaper models

## Best Practices

1. **Model Selection**
   - Start with 2-3 models for balance between cost and accuracy
   - Mix model types for diversity (e.g., GPT-3.5 + GPT-4)

2. **Document Chunking**
   - Typical chunk size: 500-1500 characters
   - Overlap: 10-20% of chunk size
   - Adjust based on document structure

3. **Retrieval Parameters**
   - top_k: 3-7 documents typically sufficient
   - Lower score_threshold for broader search
   - Higher threshold for precise answers

4. **Aggregation Strategy**
   - Use weighted_voting for general queries
   - Use majority_vote for factual questions
   - Use best_score when quality matters most
   - Use all_responses for debugging

## Extension Points

### Adding New Vector Stores
Extend `VectorStoreManager` to support additional vector databases:
- Pinecone
- Weaviate
- Milvus

### Adding New Models
Add support for other LLM providers:
- Anthropic Claude
- Cohere
- HuggingFace Transformers
- Local models

### Custom Aggregation Strategies
Implement new aggregation methods in `ResponseAggregator`:
- LLM-as-judge aggregation
- Semantic similarity-based selection
- Confidence-weighted ensembles

## Testing

### Unit Tests
Located in `tests/test_multirag.py`:
- Document processor tests
- Response aggregator tests
- Mock-based testing to avoid API calls

### Integration Tests
Recommended tests to add:
- End-to-end query pipeline
- Vector store persistence
- Multi-model parallelization

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**
   - Solution: Install dependencies with `pip install -r requirements.txt`

2. **OPENAI_API_KEY not set**
   - Solution: Set environment variable or pass to constructor

3. **Vector store not found**
   - Solution: Call `load_documents()` before querying

4. **Out of memory**
   - Solution: Reduce chunk_size or use FAISS instead of Chroma

5. **Slow queries**
   - Solution: Enable parallel processing with `use_parallel=True`

## Future Enhancements

- [ ] Support for more document formats (DOCX, HTML, Markdown)
- [ ] Streaming responses for real-time output
- [ ] Caching layer for repeated queries
- [ ] Model selection based on query type
- [ ] Fine-tuning support for custom models
- [ ] Web UI for interactive querying
- [ ] Evaluation metrics and benchmarking
- [ ] Multi-language support
