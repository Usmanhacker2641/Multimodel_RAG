# Multi-LLM RAG System - User Guide

## 🎯 Overview

This is a professional Multi-LLM RAG (Retrieval Augmented Generation) system with:
- **Parallel Multi-LLM Responses**: Get responses from Hugging Face, DeepSeek, and Gemini simultaneously
- **Multimodal Upload Support**: Process documents, images, audio files, and web URLs
- **ChatGPT-style Interface**: Clean, intuitive UI with real-time responses
- **Vector Database**: FAISS/Chroma for efficient semantic search
- **API Key Management**: Secure configuration for multiple LLM providers

---

## 🚀 Quick Start

### 1. Start the Application

Run the following command from the project root:

```bash
python run.py
```

This will start:
- **Backend API** on http://localhost:8000
- **Frontend UI** on http://localhost:8501

### 2. Configure API Keys

1. Open the application at http://localhost:8501
2. Click **⚙️ Settings & API Keys** in the sidebar
3. Enter your API keys:
   - **Hugging Face API Key**: Get from https://huggingface.co/settings/tokens
   - **DeepSeek API Key**: Get from https://platform.deepseek.com
   - **Gemini API Key**: Get from https://makersuite.google.com/app/apikey
4. Click **Save Settings**

---

## 📤 Upload Data Sources

### Navigate to Upload Page

Click **📤 Upload** in the sidebar to access the upload panel.

### Supported Upload Types

#### 1. **📄 Document Upload**
- **Supported formats**: PDF, DOCX, TXT, CSV, XLSX, PPTX
- **How to use**:
  1. Drag and drop files or click to browse
  2. Click **🚀 Process Documents**
  3. Wait for processing to complete

#### 2. **🖼️ Image Upload**
- **Supported formats**: PNG, JPG, JPEG, GIF, BMP, WEBP
- **Features**: OCR text extraction from images
- **How to use**:
  1. Upload images
  2. Click **🚀 Process Images**
  3. Text will be extracted using OCR

#### 3. **🔊 Audio Upload**
- **Supported formats**: MP3, WAV, OGG, M4A, FLAC
- **Features**: Automatic speech-to-text transcription
- **How to use**:
  1. Upload audio files
  2. Click **🚀 Process Audio**
  3. Audio will be transcribed and indexed

#### 4. **🌐 Web URL Fetch**
- **Features**: Scrape and index content from websites
- **How to use**:
  1. Enter a valid URL (starting with http:// or https://)
  2. Click **🔍 Fetch**
  3. Content will be extracted and processed

---

## 💬 Chat Interface

### Ask Questions

1. Navigate to **💬 Chat** page
2. Type your question in the chat input
3. Press Enter or click Send

### Response Flow

1. **Context Retrieval**: System searches vector database for relevant chunks
2. **Multi-LLM Processing**: Sends query to all selected models in parallel
3. **Response Aggregation**: Combines responses into a final answer
4. **Display**: Shows aggregated answer and individual model responses

### Model Selection

In the sidebar, you can enable/disable specific models:
- ✅ **Mistral 7B** (HuggingFace)
- ✅ **DeepSeek Chat**
- ✅ **Gemini Pro**
- ⬜ **Falcon 7B** (HuggingFace)
- ⬜ **Zephyr 7B** (HuggingFace)

---

## ⚙️ Settings & Configuration

### API Keys

Configure your LLM provider API keys in the Settings page:

```
HuggingFace API Key: hf_xxxxxxxxxxxxxxxxxx
DeepSeek API Key: sk-xxxxxxxxxxxxxxxxxx
Gemini API Key: AIzaSyxxxxxxxxxxxxxxxxxx
```

### Model Parameters

- **Temperature** (0.0 - 2.0): Controls response randomness
- **Max Tokens** (100 - 32000): Maximum response length

### RAG Settings

- **Chunk Size** (100 - 5000): Size of text chunks for indexing
- **Top-K Chunks** (1 - 20): Number of relevant chunks to retrieve

---

## 🔧 Technical Architecture

### Backend (FastAPI)

**Endpoints:**
- `POST /api/upload/` - Upload and process files, URLs, text
- `POST /api/query/` - Submit queries for RAG processing
- `GET /api/history/` - Retrieve chat history
- `GET /api/models/` - Get available models

**File Location**: `backend/main.py`

### Frontend (Streamlit)

**Components:**
- **Chat Interface**: `frontend/components/chat_interface.py`
- **Upload Panel**: `frontend/upload_panel.py`
- **Settings Panel**: `frontend/components/settings_panel.py`
- **API Client**: `frontend/api_client.py`

### Services

1. **Multi-LLM Runner** (`services/multi_llm_runner.py`)
   - Parallel execution of multiple LLM APIs
   - Supports HuggingFace, DeepSeek, Gemini
   - Error handling and fallbacks

2. **Embedder** (`services/embedder.py`)
   - Converts text to vector embeddings
   - Uses SentenceTransformers

3. **Vector Manager** (`vectorstore/vector_manager.py`)
   - Manages FAISS/Chroma vector databases
   - Similarity search

4. **File Parser** (`services/file_parser.py`)
   - Extracts text from various file types
   - Integrates with ASR/OCR models

5. **ASR Model** (`models/asr_model.py`)
   - Whisper-based speech recognition
   - Audio transcription

6. **OCR Model** (`models/ocr_model.py`)
   - Tesseract/Donut-based text extraction
   - Image processing

### Pipeline Flow

```
Upload → File Parser → Chunker → Embedder → Vector DB
                                                ↓
Query → Retriever → Multi-LLM Runner → Aggregator → Response
```

---

## 📊 API Status Indicators

The sidebar shows real-time API status:

```
🔑 API Status
- HuggingFace: ✅/❌
- DeepSeek: ✅/❌
- Gemini: ✅/❌
```

- ✅ = API key configured
- ❌ = API key missing

---

## 🎨 Features

### ✅ Completed Features

1. **Multi-LLM Support**: Parallel responses from multiple providers
2. **Multimodal Uploads**: Documents, images, audio, URLs
3. **Vector Search**: Efficient semantic retrieval
4. **Chat Interface**: Clean, responsive UI
5. **API Key Management**: Secure configuration
6. **Session Management**: Persistent chat history
7. **File Processing**: Support for 15+ file types
8. **Real-time Status**: Processing indicators and feedback

### 🔮 Future Enhancements

- User authentication
- Advanced RAG techniques (HyDE, Query Decomposition)
- Custom model fine-tuning
- Export chat history
- Analytics dashboard

---

## 🐛 Troubleshooting

### Backend Not Starting

```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process if needed
taskkill /PID <process_id> /F
```

### API Connection Errors

- Ensure backend is running on http://localhost:8000
- Check CORS settings in `backend/main.py`
- Verify API keys are correctly entered

### File Upload Failures

- Check file size (max 50MB)
- Verify file format is supported
- Check backend logs for detailed errors

### LLM Response Issues

- Verify API keys are valid and active
- Check API rate limits
- Review model availability (some may require paid plans)

---

## 📝 API Key Resources

### HuggingFace
- Sign up: https://huggingface.co/join
- Get API key: https://huggingface.co/settings/tokens
- Free tier available with rate limits

### DeepSeek
- Sign up: https://platform.deepseek.com
- Get API key: Dashboard → API Keys
- Affordable pricing with pay-as-you-go

### Google Gemini
- Sign up: https://makersuite.google.com
- Get API key: https://makersuite.google.com/app/apikey
- Free tier available (60 requests/minute)

---

## 💡 Best Practices

1. **Upload Strategy**:
   - Process related documents together
   - Use clear, descriptive filenames
   - Organize by topic/domain

2. **Query Optimization**:
   - Be specific in questions
   - Use natural language
   - Reference uploaded content when possible

3. **Model Selection**:
   - Enable multiple models for diverse perspectives
   - Disable unused models to save API costs
   - Test different combinations for best results

4. **Performance**:
   - Upload files during off-peak hours for large batches
   - Clear cache periodically
   - Monitor API usage and costs

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review backend logs: `backend/main.py`
3. Check frontend console: Browser DevTools
4. Review API documentation: http://localhost:8000/docs

---

## 📄 License

This project is for educational and research purposes.

---

**Enjoy your Multi-LLM RAG System! 🚀**
