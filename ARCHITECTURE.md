# System Architecture & Connection Map

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Streamlit)                         │
│                     http://localhost:8501                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ Chat Page    │  │ Upload Page  │  │ Settings Page│              │
│  │              │  │              │  │              │              │
│  │ - Messages   │  │ - Documents  │  │ - API Keys   │              │
│  │ - Input      │  │ - Images     │  │ - Parameters │              │
│  │ - Responses  │  │ - Audio      │  │ - Models     │              │
│  │              │  │ - URLs       │  │              │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                 │                 │                       │
│         └─────────────────┼─────────────────┘                       │
│                           │                                         │
│                    ┌──────▼──────┐                                  │
│                    │ API Client  │                                  │
│                    │             │                                  │
│                    │ - query_rag │                                  │
│                    │ - upload_*  │                                  │
│                    └──────┬──────┘                                  │
└───────────────────────────┼─────────────────────────────────────────┘
                            │ HTTP Requests
                            │
┌───────────────────────────▼─────────────────────────────────────────┐
│                     BACKEND (FastAPI)                                │
│                   http://localhost:8000                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │Query Routes  │  │Upload Routes │  │History Routes│              │
│  │              │  │              │  │              │              │
│  │POST /query/  │  │POST /upload/ │  │GET /history/ │              │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘              │
│         │                 │                                         │
│         └─────────────────┼──────────┐                              │
│                           │          │                              │
│                    ┌──────▼──────────▼─┐                            │
│                    │   Full Pipeline    │                            │
│                    │                   │                            │
│                    │  - process()      │                            │
│                    │  - query()        │                            │
│                    └──────┬────────────┘                            │
└───────────────────────────┼─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        SERVICE LAYER                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐        │
│  │ File Parser    │  │ Text Processor │  │    Chunker     │        │
│  │                │  │                │  │                │        │
│  │ - PDF          │  │ - Clean text   │  │ - Split text   │        │
│  │ - DOCX         │  │ - Deduplicate  │  │ - Overlap      │        │
│  │ - Audio (ASR)  │  │ - Normalize    │  │ - Metadata     │        │
│  │ - Image (OCR)  │  │                │  │                │        │
│  └────────┬───────┘  └────────┬───────┘  └────────┬───────┘        │
│           │                   │                   │                 │
│           └───────────────────┼───────────────────┘                 │
│                               │                                     │
│                        ┌──────▼──────┐                              │
│                        │  Embedder   │                              │
│                        │             │                              │
│                        │ Sentence    │                              │
│                        │ Transformers│                              │
│                        └──────┬──────┘                              │
│                               │                                     │
│                        ┌──────▼──────┐                              │
│                        │Vector Manager│                              │
│                        │             │                              │
│                        │ FAISS/Chroma│                              │
│                        └──────┬──────┘                              │
└───────────────────────────────┼─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         QUERY PROCESSING                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  User Query                                                          │
│      │                                                               │
│      ▼                                                               │
│  ┌──────────┐                                                        │
│  │Retriever │ ──► Vector Search ──► Top-K Chunks                    │
│  └──────────┘                                                        │
│      │                                                               │
│      ▼                                                               │
│  ┌─────────────────────┐                                            │
│  │ Multi-LLM Runner    │                                            │
│  │                     │                                            │
│  │  Parallel Execution │                                            │
│  │  ┌─────────────────┐│                                            │
│  │  │ HuggingFace API ││ ──► Mistral 7B / Falcon / Zephyr          │
│  │  └─────────────────┘│                                            │
│  │  ┌─────────────────┐│                                            │
│  │  │ DeepSeek API    ││ ──► DeepSeek Chat / Coder                 │
│  │  └─────────────────┘│                                            │
│  │  ┌─────────────────┐│                                            │
│  │  │ Gemini API      ││ ──► Gemini Pro / Pro Vision               │
│  │  └─────────────────┘│                                            │
│  └──────────┬──────────┘                                            │
│             │                                                        │
│             ▼                                                        │
│  ┌─────────────────────┐                                            │
│  │  Aggregator LLM     │                                            │
│  │                     │                                            │
│  │  Combines responses │                                            │
│  │  into final answer  │                                            │
│  └──────────┬──────────┘                                            │
│             │                                                        │
│             ▼                                                        │
│  Final Response to User                                             │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔗 API Connection Flow

### 1. Upload Flow

```
User Upload (Frontend)
    │
    ▼
frontend/upload_panel.py
    │
    ▼
frontend/api_client.py
    │ (HTTP POST)
    ▼
backend/upload_routers.py
    │
    ▼
pipelines/full_pipeline.py::process()
    │
    ├──► services/file_parser.py
    │    ├──► models/asr_model.py (audio)
    │    └──► models/ocr_model.py (images)
    │
    ├──► services/text_preprocessor.py
    ├──► services/chunker.py
    ├──► services/embedder.py
    │
    └──► vectorstore/vector_manager.py
         └──► Store in FAISS/Chroma
```

### 2. Query Flow

```
User Question (Frontend)
    │
    ▼
frontend/components/chat_interface.py
    │ (with API keys from session)
    ▼
frontend/api_client.py::query_rag()
    │ (HTTP POST with form data)
    ▼
backend/query_routes.py
    │ (extracts API keys)
    ▼
pipelines/full_pipeline.py::query()
    │
    ├──► services/retriever.py
    │    └──► vectorstore/vector_manager.py
    │         └──► Returns top-K chunks
    │
    ├──► services/multi_llm_runner.py
    │    │ (parallel execution with API keys)
    │    ├──► HuggingFace API
    │    ├──► DeepSeek API
    │    └──► Gemini API
    │         └──► Returns multiple responses
    │
    └──► services/aggregator_llm.py
         └──► Combines into final answer
              │
              ▼
         Response back to Frontend
```

### 3. Settings Flow

```
User enters API Keys (Frontend)
    │
    ▼
frontend/components/settings_panel.py
    │
    └──► Stores in st.session_state
         ├── hf_api_key
         ├── deepseek_api_key
         └── gemini_api_key
              │
              ▼
         Used in every query request
```

---

## 📁 File Structure

```
Multimodel_RAG/
│
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── query_routes.py          # POST /query/ endpoint
│   ├── upload_routers.py        # POST /upload/ endpoint
│   ├── history_routes.py        # GET /history/ endpoint
│   ├── feedback_routes.py       # Feedback endpoints
│   └── model_routes.py          # Model info endpoints
│
├── frontend/
│   ├── app.py                   # Streamlit main app
│   ├── api_client.py            # HTTP client for backend
│   ├── upload_panel.py          # Upload UI
│   ├── styles.py                # CSS styling
│   └── components/
│       ├── chat_interface.py    # Chat UI
│       ├── settings_panel.py    # Settings UI
│       └── sidebar.py           # Sidebar (legacy)
│
├── services/
│   ├── multi_llm_runner.py      # 🔥 Parallel LLM execution
│   ├── aggregator_llm.py        # Response aggregation
│   ├── embedder.py              # Text → Vectors
│   ├── retriever.py             # Vector search
│   ├── chunker.py               # Text splitting
│   ├── text_preprocessor.py     # Text cleaning
│   ├── file_parser.py           # File → Text
│   └── dbscan_category.py       # Clustering
│
├── models/
│   ├── asr_model.py             # Audio → Text (Whisper)
│   └── ocr_model.py             # Image → Text (Tesseract)
│
├── pipelines/
│   └── full_pipeline.py         # 🔥 Main orchestration
│
├── vectorstore/
│   └── vector_manager.py        # FAISS/Chroma wrapper
│
├── database/
│   └── db_client.py             # SQLite for history
│
├── run.py                       # Start script
├── requirements.txt             # Python dependencies
├── USER_GUIDE.md               # This guide
└── README.md                    # Project readme
```

---

## 🔑 API Key Flow

### How API Keys Travel Through the System

1. **User Input** (Settings Page)
   ```python
   # frontend/components/settings_panel.py
   st.text_input("Hugging Face API Key", type="password")
   st.session_state.hf_api_key = hf_api_key
   ```

2. **Query Preparation** (Chat Interface)
   ```python
   # frontend/components/chat_interface.py
   api_keys = {
       "hf_api_key": st.session_state.get("hf_api_key"),
       "deepseek_api_key": st.session_state.get("deepseek_api_key"),
       "gemini_api_key": st.session_state.get("gemini_api_key")
   }
   ```

3. **HTTP Request** (API Client)
   ```python
   # frontend/api_client.py
   data = {
       "question": question,
       "hf_api_key": api_keys["hf_api_key"],
       # ... other keys
   }
   response = requests.post(f"{BASE_URL}/query/", data=data)
   ```

4. **Backend Reception** (Query Routes)
   ```python
   # backend/query_routes.py
   @router.post("/")
   async def query_rag(
       question: str = Form(...),
       hf_api_key: Optional[str] = Form(None),
       # ... other params
   ):
       api_keys = {"hf_api_key": hf_api_key, ...}
       result = pipeline.query(question, api_keys=api_keys)
   ```

5. **Pipeline Processing** (Full Pipeline)
   ```python
   # pipelines/full_pipeline.py
   def query(self, query_text: str, api_keys: Optional[Dict] = None):
       multi_llm_answers = run_multi_llm(
           query_text, retrieved_chunks, selected_models, api_keys
       )
   ```

6. **LLM Execution** (Multi-LLM Runner)
   ```python
   # services/multi_llm_runner.py
   def _call_huggingface_api(model_config, prompt, context, api_keys):
       api_key = api_keys.get("hf_api_key") if api_keys else None
       headers = {"Authorization": f"Bearer {api_key}"}
       # Make API call
   ```

---

## 🌐 Endpoint Reference

### Backend API Endpoints

| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|------------|
| `/` | GET | Health check | None |
| `/api/upload/` | POST | Upload files/URLs | file, text, url |
| `/api/query/` | POST | Submit query | question, mode, top_k, API keys |
| `/api/history/` | GET | Get chat history | session_id, limit |
| `/api/models/` | GET | List available models | None |

### Frontend Pages

| Page | Route | Purpose |
|------|-------|---------|
| Chat | `page=Chat` | Ask questions and view responses |
| Upload | `page=Upload` | Upload files, images, audio, URLs |
| Settings | `page=Settings` | Configure API keys and parameters |

---

## 🔄 Data Flow Examples

### Example 1: PDF Upload

```
1. User uploads "report.pdf" → Upload Panel
2. upload_panel.py → upload_file_bytes(pdf_bytes, "report.pdf")
3. api_client.py → POST /api/upload/ (file=pdf_bytes)
4. upload_routers.py → Saves temp file
5. full_pipeline.py → process({"file_path": "/tmp/report.pdf"})
6. file_parser.py → extract_text_from_file() using PyPDF2
7. text_preprocessor.py → Clean and normalize
8. chunker.py → Split into chunks
9. embedder.py → Convert to vectors
10. vector_manager.py → Store in FAISS
11. Response → {"status": "success", "chunks": 45}
12. UI → Display success message
```

### Example 2: Query Processing

```
1. User asks "What is the revenue?" → Chat Interface
2. chat_interface.py → query_rag(question, api_keys)
3. api_client.py → POST /query/ (question + API keys)
4. query_routes.py → Extract parameters
5. full_pipeline.py → query(question, api_keys)
6. retriever.py → Search vector DB → Top 5 chunks
7. multi_llm_runner.py → Parallel execution:
   - Thread 1: Call HuggingFace API
   - Thread 2: Call DeepSeek API
   - Thread 3: Call Gemini API
8. Collect responses: [response1, response2, response3]
9. aggregator_llm.py → Combine responses
10. Response → {final_answer, multi_llm_answers, chunks}
11. UI → Display in chat
```

---

## 🎯 Key Components Explained

### 1. Multi-LLM Runner
- **Location**: `services/multi_llm_runner.py`
- **Purpose**: Execute multiple LLM APIs in parallel
- **Features**:
  - ThreadPoolExecutor for concurrency
  - Error handling and fallbacks
  - Stub responses when API unavailable
  - Structured response format

### 2. Full Pipeline
- **Location**: `pipelines/full_pipeline.py`
- **Purpose**: Orchestrate entire RAG workflow
- **Methods**:
  - `process()`: Ingest and index data
  - `query()`: Retrieve and generate answers

### 3. Vector Manager
- **Location**: `vectorstore/vector_manager.py`
- **Purpose**: Manage vector database
- **Supported**: FAISS, Chroma
- **Operations**: Add, search, delete embeddings

### 4. API Client
- **Location**: `frontend/api_client.py`
- **Purpose**: Centralized HTTP communication
- **Features**:
  - Error handling
  - Timeout management
  - Request formatting

---

## 🚀 Performance Optimization

### Parallel LLM Execution
- All LLM APIs called simultaneously
- Reduces total response time
- Configurable timeout (30s default)

### Vector Search
- FAISS: Fast approximate nearest neighbor search
- Chroma: Persistent vector storage
- Efficient retrieval even with millions of chunks

### Caching
- Transcription caching for audio files
- OCR result caching for images
- Session state for UI performance

---

**This architecture enables a scalable, efficient, and user-friendly Multi-LLM RAG system! 🎉**
