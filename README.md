# 🚀 Multi-LLM RAG System

A **professional, production-ready Multi-LLM Retrieval-Augmented Generation (RAG)** system with parallel LLM processing, multimodal upload support, and a ChatGPT-style interface.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-brightgreen.svg)
![Status](https://img.shields.io/badge/status-production-success.svg)

---

## ✨ Key Features

### 🤖 Multi-LLM Parallel Processing
- **3+ LLM Providers**: HuggingFace, DeepSeek, Google Gemini
- **Parallel Execution**: Get responses from all models simultaneously
- **Response Aggregation**: Combine insights from multiple perspectives
- **5+ Models**: Mistral 7B, Falcon 7B, Zephyr 7B, DeepSeek Chat/Coder, Gemini Pro/Vision

### 📤 Multimodal Upload Support
- **📄 Documents**: PDF, DOCX, TXT, CSV, XLSX, PPTX
- **🖼️ Images**: PNG, JPG, JPEG, GIF, BMP, WEBP (with OCR)
- **🔊 Audio**: MP3, WAV, OGG, M4A, FLAC (with ASR transcription)
- **🌐 Web URLs**: Automatic content scraping and indexing

### 🎨 Professional UI
- **ChatGPT-Style Interface**: Clean, intuitive, responsive
- **Three Main Pages**: Chat, Upload, Settings
- **Real-time Status**: Processing indicators and API status
- **Multi-Model Display**: See individual responses and aggregated answers
- **Secure API Management**: Password-protected key storage

### � Advanced RAG Pipeline
- **Vector Search**: FAISS/Chroma for efficient semantic retrieval
- **Smart Chunking**: Intelligent text segmentation with overlap
- **Embeddings**: SentenceTransformers for high-quality vectors
- **Context-Aware**: Retrieves most relevant chunks for each query
- **Category Detection**: DBSCAN clustering for better organization

---

## 🚀 Quick Start

### 1. Installation

```powershell
# Clone or navigate to the project
cd Multimodel_RAG

# Install dependencies
pip install -r requirements.txt
```

### 2. Launch Application

```powershell
# Start both backend and frontend
python run.py
```

This opens:
- **Backend API**: http://localhost:8000
- **Frontend UI**: http://localhost:8501

### 3. Configure API Keys

1. Open http://localhost:8501
2. Go to **⚙️ Settings & API Keys**
3. Enter your API keys:
   - **HuggingFace**: https://huggingface.co/settings/tokens
   - **DeepSeek**: https://platform.deepseek.com
   - **Gemini**: https://makersuite.google.com/app/apikey
4. Click **Save Settings**

> Without API keys, the system uses stub responses for testing.

### 4. Upload & Chat

**Upload Data**:
- Click **📤 Upload**
- Choose file type (documents, images, audio, URLs)
- Upload and process

**Start Chatting**:
- Click **💬 Chat**
- Select models in sidebar
- Ask questions about your uploaded data

---

## � Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide (start here!)
- **[USER_GUIDE.md](USER_GUIDE.md)** - Comprehensive user manual
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture & connections
- **[COMPLETE.md](COMPLETE.md)** - Feature summary & capabilities

---

## 🎯 Usage Examples

### Example 1: Document Analysis
```
1. Upload: quarterly_report.pdf
2. Ask: "What were the key financial highlights in Q4?"
3. Get: Multi-model responses with context from the document
```

### Example 2: Image Analysis
```
1. Upload: chart.png
2. Ask: "Explain the trends shown in this chart"
3. Get: OCR-extracted text analyzed by multiple LLMs
```

### Example 3: Audio Transcription
```
1. Upload: meeting_recording.mp3
2. Ask: "What were the action items from the meeting?"
3. Get: ASR transcription analyzed for key points
```

### Example 4: Web Research
```
1. Enter URL: https://example.com/article
2. Ask: "Summarize the main arguments"
3. Get: Scraped content analyzed by multiple models
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│            Frontend (Streamlit)                      │
│  Chat | Upload | Settings                            │
└──────────────────┬──────────────────────────────────┘
                   │ HTTP/REST
┌──────────────────▼──────────────────────────────────┐
│             Backend (FastAPI)                        │
│  Upload Routes | Query Routes | History Routes      │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│              Full Pipeline                           │
│  Process | Query | Retrieve | Aggregate             │
└──────────────────┬──────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼────┐  ┌──────▼──────┐  ┌───▼────────┐
│ File   │  │  Vector DB  │  │ Multi-LLM  │
│ Parser │  │ FAISS/Chroma│  │  Runner    │
│        │  │             │  │            │
│ ASR/OCR│  │  Embedder   │  │ HF/DS/GM   │
└────────┘  └─────────────┘  └────────────┘
│  │  Preprocessor → Chunker → Embedder →         │   │
│  │  VectorDB → Retriever → MultiLLM → Aggregator│   │
│  └──────────────────────────────────────────────┘   │
└────────┬────────────────┬──────────────────┬─────────┘
         │                │                  │
┌────────▼──────┐  ┌──────▼────────┐  ┌──────▼─────────┐
│  Vector Store │  │  SQLite DB    │  │  Cloud DB      │
│  (FAISS/      │  │  (Chat        │  │  (Supabase/    │
│   Chroma)     │  │   History)    │  │   MongoDB)     │
└───────────────┘  └───────────────┘  └────────────────┘
```

## 📂 Project Structure

```
Multimodel_RAG/
├── backend/
│   ├── main.py                 # FastAPI app entry
│   ├── upload_routers.py       # File/URL upload endpoints
│   ├── query_routes.py         # RAG query endpoints
│   ├── history_routes.py       # Chat history API
│   ├── feedback_routes.py      # User feedback
│   └── model_routes.py         # Model management
├── frontend/
│   ├── app.py                  # Streamlit main app
│   ├── api_client.py           # Backend API connector
│   ├── components/
│   │   ├── chat_interface.py  # Chat UI
│   │   ├── sidebar.py          # Navigation sidebar
│   │   └── analytics_panel.py  # Analytics dashboard
│   ├── upload_panel.py         # Upload interface
│   └── styles.py               # Custom CSS
├── pipelines/
│   └── full_pipeline.py        # End-to-end RAG pipeline
├── services/
│   ├── text_preprocessor.py   # Text cleaning
│   ├── chunker.py              # Document chunking
│   ├── embedder.py             # Embedding generation
│   ├── retriever.py            # Vector search
│   ├── multi_llm_runner.py    # Multi-model execution
│   ├── aggregator_llm.py      # Response aggregation
│   ├── dbscan_category.py     # Clustering & classification
│   └── file_parser.py          # Multimodal parsing
├── vectorstore/
│   └── vector_manager.py       # Vector DB abstraction
├── database/
│   ├── db_client.py            # Database wrapper
│   └── chat_history_dao.py     # SQLite persistence
├── run.py                      # Application launcher
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## ⚙️ Configuration

### Environment Variables
Create a `.env` file:

```env
# Vector Database
VECTOR_DB=faiss  # or "chroma"

# Database (optional)
DB_TYPE=sqlite  # or "mongodb", "supabase"
SQLITE_DB_PATH=./chat_history.db

# MongoDB (if using)
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
DB_NAME=multimodel_rag

# Supabase (if using)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# API Configuration
API_URL=http://localhost:8000/api
```

## 🧪 Testing

```powershell
# Test the backend
python -m pytest

# Test upload functionality
# Upload a sample document through the UI and verify it appears in the vector store

# Test query functionality
# Ask a question related to your uploaded documents
```

## 📊 Key Components

### FullPipeline
Orchestrates the complete RAG flow:
- **process()**: Ingests and indexes documents
- **query()**: Retrieves context and generates responses

### Multi-LLM Runner
Executes queries across multiple models in parallel, returning structured responses with confidence scores.

### Aggregator LLM
Synthesizes multiple model outputs into a coherent final answer using reasoning.

### DBSCAN Category
Clusters embeddings to automatically detect content categories for smarter retrieval.

---

**Built with ❤️ for high-accuracy multi-model RAG**

