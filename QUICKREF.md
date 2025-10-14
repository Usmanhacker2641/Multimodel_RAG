# MultiRAG Quick Reference

## Installation

```bash
pip install -r requirements.txt
export OPENAI_API_KEY='your-api-key'
```

## Basic Usage

### Python API

```python
from multirag import MultiRAG

# Initialize
rag = MultiRAG(config_path="config.yaml")

# Load documents
rag.load_documents("documents/")

# Query
result = rag.query("What is artificial intelligence?")
print(result['response'])
```

### Command Line

```bash
# Load documents
python cli.py --load documents/

# Query
python cli.py --query "What is AI?" --show-sources

# Load existing vector store
python cli.py --load-existing --query "What is ML?"
```

## Configuration Quick Setup

```yaml
# Minimal config.yaml
models:
  - name: "gpt-3.5-turbo"
    provider: "openai"
    temperature: 0.7
    max_tokens: 500
    enabled: true

vector_store:
  type: "chroma"
  embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
  chunk_size: 1000
  chunk_overlap: 200

aggregation:
  strategy: "weighted_voting"
  weights:
    gpt-3.5-turbo: 1.0
```

## Aggregation Strategies

| Strategy | Use Case | Code |
|----------|----------|------|
| Weighted Voting | General purpose, trust certain models more | `strategy: "weighted_voting"` |
| Majority Vote | Democratic approach, factual questions | `strategy: "majority_vote"` |
| Best Score | Single best answer, quality over consensus | `strategy: "best_score"` |
| All Responses | Debugging, comparison | `strategy: "all_responses"` |

## Common Patterns

### Pattern 1: Simple Q&A

```python
from multirag import MultiRAG

rag = MultiRAG()
rag.load_documents("docs/")
answer = rag.query("What is X?")
print(answer['response'])
```

### Pattern 2: Query with Sources

```python
result = rag.query_with_sources("Explain Y")
print(f"Answer: {result['response']}")
print(f"Confidence: {result['confidence']:.2f}")

for source in result['formatted_sources']:
    print(f"\nSource {source['source_id']}: {source['content']}")
```

### Pattern 3: Multiple Queries

```python
questions = ["What is A?", "What is B?", "What is C?"]

for q in questions:
    result = rag.query(q)
    print(f"Q: {q}")
    print(f"A: {result['response']}\n")
```

### Pattern 4: Sequential Processing

```python
# For API rate limiting
result = rag.query("What is Z?", use_parallel=False)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No API key | `export OPENAI_API_KEY='key'` |
| Module not found | `pip install -r requirements.txt` |
| Vector store not found | Call `load_documents()` first |
| Slow queries | Use `use_parallel=True` |
| High costs | Reduce number of enabled models |

## Environment Variables

```bash
export OPENAI_API_KEY='your-key'
# Optional
export DEFAULT_MODEL='gpt-3.5-turbo'
export VECTOR_STORE_DIR='./chroma_db'
```

## Response Structure

```python
{
    'response': str,              # Aggregated answer
    'primary_model': str,         # Main model used
    'models_used': list,          # All models queried
    'confidence': float,          # 0.0-1.0
    'strategy': str,              # Aggregation strategy
    'sources': list,              # Source documents
    'formatted_sources': list     # Formatted sources (with query_with_sources)
}
```

## Performance Tips

1. **Use parallel processing** (default): 3x faster with 3 models
2. **Cache vector store**: Load once, query many times
3. **Optimize chunk size**: 1000 chars works well for most cases
4. **Limit top_k**: 5 documents usually sufficient
5. **Use cheaper models first**: Mix GPT-3.5 (cheap) with GPT-4 (expensive)

## File Structure

```
Multimodel_RAG/
├── multirag/              # Main package
│   ├── multi_rag.py      # Core orchestrator
│   ├── document_processor.py
│   ├── vector_store_manager.py
│   └── response_aggregator.py
├── tests/                # Unit tests
├── config.yaml           # Configuration
├── example.py            # Usage examples
├── cli.py               # CLI interface
└── requirements.txt      # Dependencies
```

## API Reference

### MultiRAG Class

```python
MultiRAG(config_path=None, api_key=None)
  .load_documents(file_path)
  .load_existing_vector_store()
  .query(question, use_parallel=True)
  .query_with_sources(question)
```

### DocumentProcessor Class

```python
DocumentProcessor(chunk_size=1000, chunk_overlap=200)
  .load_documents(file_path)
  .chunk_documents(documents)
  .process_documents(file_path)
  .process_text(text)
```

### VectorStoreManager Class

```python
VectorStoreManager(store_type="chroma", embedding_model=..., ...)
  .create_vector_store(documents)
  .load_vector_store()
  .add_documents(documents)
  .similarity_search(query, k=5, score_threshold=None)
  .as_retriever(k=5)
```

### ResponseAggregator Class

```python
ResponseAggregator(strategy="weighted_voting", weights=None)
  .aggregate(responses)
  .calculate_confidence(responses)
```

## Examples

See `example.py` for complete working examples of:
- Loading documents
- Querying multiple models
- Different aggregation strategies
- Source document retrieval
- Loading existing vector stores

Run with:
```bash
python example.py
```
