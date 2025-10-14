# Multimodel_RAG

A Multi-Model Retrieval-Augmented Generation (RAG) system that queries multiple language models in parallel and aggregates their responses to provide high-accuracy answers.

## Features

- 🚀 **Parallel Processing**: Query multiple models simultaneously for faster responses
- 🎯 **High Accuracy**: Aggregate responses from multiple models using various strategies
- 📚 **Document Processing**: Load and process documents from various formats (PDF, TXT)
- 🔍 **Vector Store Integration**: Efficient document retrieval using Chroma or FAISS
- ⚙️ **Flexible Configuration**: YAML-based configuration for easy customization
- 🤖 **Multiple Model Support**: Support for various OpenAI models (GPT-3.5, GPT-4, etc.)
- 📊 **Multiple Aggregation Strategies**: Weighted voting, majority vote, best score, or all responses

## Architecture

```
┌─────────────┐
│   Query     │
└──────┬──────┘
       │
       v
┌─────────────────────────────────┐
│  Document Retrieval             │
│  (Vector Store Search)          │
└──────┬──────────────────────────┘
       │
       v
┌─────────────────────────────────┐
│  Parallel Model Queries         │
├─────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐      │
│  │ Model 1 │  │ Model 2 │ ...  │
│  └────┬────┘  └────┬────┘      │
└───────┼────────────┼────────────┘
        │            │
        v            v
┌─────────────────────────────────┐
│  Response Aggregator            │
│  (Weighted Voting/Best Score)   │
└──────┬──────────────────────────┘
       │
       v
┌─────────────┐
│   Result    │
└─────────────┘
```

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Usmanhacker2641/Multimodel_RAG.git
cd Multimodel_RAG
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

Or create a `.env` file:
```
OPENAI_API_KEY=your-api-key-here
```

## Quick Start

### Basic Usage

```python
from multirag import MultiRAG

# Initialize the system
rag = MultiRAG(config_path="config.yaml")

# Load documents
rag.load_documents("path/to/your/documents")

# Query the system
result = rag.query("What is artificial intelligence?")
print(result['response'])
```

### Advanced Usage

```python
from multirag import MultiRAG

# Initialize with custom API key
rag = MultiRAG(api_key="your-openai-api-key")

# Load documents
rag.load_documents("documents/")

# Query with sources
result = rag.query_with_sources("Explain machine learning")

print("Response:", result['response'])
print("Confidence:", result['confidence'])
print("Models used:", result['models_used'])

if 'formatted_sources' in result:
    for source in result['formatted_sources']:
        print(f"\nSource {source['source_id']}:")
        print(source['content'])
```

## Configuration

Edit `config.yaml` to customize the system:

```yaml
# Models to use in parallel
models:
  - name: "gpt-3.5-turbo"
    provider: "openai"
    temperature: 0.7
    max_tokens: 500
    enabled: true

# Vector store configuration
vector_store:
  type: "chroma"  # or "faiss"
  embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
  chunk_size: 1000
  chunk_overlap: 200

# Retrieval settings
retrieval:
  top_k: 5
  score_threshold: 0.5

# Aggregation strategy
aggregation:
  strategy: "weighted_voting"  # Options: weighted_voting, majority_vote, best_score, all_responses
  weights:
    gpt-3.5-turbo: 1.0
    gpt-4: 1.5
```

## Aggregation Strategies

### 1. Weighted Voting
Selects the response with the highest weighted score based on model weights.

```python
# In config.yaml
aggregation:
  strategy: "weighted_voting"
  weights:
    gpt-3.5-turbo: 1.0
    gpt-4: 1.5
```

### 2. Majority Vote
Selects the most common response among all models.

```python
aggregation:
  strategy: "majority_vote"
```

### 3. Best Score
Selects the response with the highest confidence score.

```python
aggregation:
  strategy: "best_score"
```

### 4. All Responses
Returns all responses from all models.

```python
aggregation:
  strategy: "all_responses"
```

## Module Structure

```
multirag/
├── __init__.py                  # Package initialization
├── multi_rag.py                 # Main MultiRAG orchestrator
├── document_processor.py        # Document loading and chunking
├── vector_store_manager.py      # Vector store management
└── response_aggregator.py       # Response aggregation strategies
```

## Components

### 1. DocumentProcessor
Handles document loading and chunking.

```python
from multirag import DocumentProcessor

processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)
documents = processor.process_documents("path/to/docs")
```

### 2. VectorStoreManager
Manages vector stores for document retrieval.

```python
from multirag import VectorStoreManager

store_manager = VectorStoreManager(store_type="chroma")
store_manager.create_vector_store(documents)
```

### 3. ResponseAggregator
Aggregates responses from multiple models.

```python
from multirag import ResponseAggregator

aggregator = ResponseAggregator(strategy="weighted_voting")
result = aggregator.aggregate(responses)
```

## Examples

Run the example script:

```bash
python example.py
```

This demonstrates:
- Loading documents
- Querying multiple models in parallel
- Different aggregation strategies
- Retrieving source documents

## Supported Document Formats

- **Text files** (`.txt`)
- **PDF files** (`.pdf`)
- **Directories** (processes all supported files)

## Performance

The system uses parallel processing to query multiple models simultaneously, significantly reducing response time compared to sequential querying.

Example timing (3 models):
- Sequential: ~6 seconds
- Parallel: ~2 seconds (3x speedup)

## Use Cases

1. **Question Answering**: Get high-quality answers by combining multiple models
2. **Document Search**: Efficiently search through large document collections
3. **Research Assistant**: Query technical documents with high accuracy
4. **Customer Support**: Provide accurate responses with source citations
5. **Knowledge Base**: Build intelligent knowledge base systems

## Limitations

- Requires OpenAI API key and credits
- Parallel querying increases API costs (multiple models per query)
- Quality depends on the underlying models used

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Citation

If you use this project in your research, please cite:

```
@software{multimodel_rag,
  title = {Multimodel RAG: Multi-Model Retrieval-Augmented Generation System},
  author = {Usman Hacker},
  year = {2025},
  url = {https://github.com/Usmanhacker2641/Multimodel_RAG}
}
```

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Acknowledgments

Built with:
- [LangChain](https://python.langchain.com/)
- [OpenAI](https://openai.com/)
- [Chroma](https://www.trychroma.com/)
- [HuggingFace](https://huggingface.co/)
