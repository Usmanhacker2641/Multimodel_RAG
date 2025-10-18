# 🚀 Startup Checklist & Quick Start Guide

## Pre-Launch Checklist

### ✅ System Requirements
- [ ] Python 3.10 or higher installed
- [ ] Minimum 8GB RAM available
- [ ] At least 2GB disk space free
- [ ] Internet connection (for downloading models)

### ✅ Installation Verification
```powershell
# 1. Navigate to project
cd Multimodel_RAG

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 3. Verify dependencies
pip list | Select-String -Pattern "fastapi|streamlit|transformers"
```

Expected output should include:
- fastapi==0.104.1
- streamlit==1.29.0
- transformers==4.35.2

---

## 🎯 Launch Options

### Option 1: Automated Launch (Recommended)
```powershell
python run.py
```
This will:
- Start backend on port 8000
- Start frontend on port 8501
- Open browser automatically

### Option 2: Manual Launch
```powershell
# Terminal 1 - Backend
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Frontend
python -m streamlit run frontend/app.py --server.port 8501
```

---

## 🧪 First-Time Setup & Testing

### 1. Verify Backend is Running
Open: http://localhost:8000/docs

You should see the FastAPI interactive API documentation.

### 2. Test Upload Functionality
```powershell
# Create a test file
"This is a test document about artificial intelligence." | Out-File -FilePath test.txt

# Upload via API (using PowerShell)
curl -X POST "http://localhost:8000/api/upload/" `
  -F "file=@test.txt"
```

Expected response:
```json
{
  "status": "success",
  "message": "Processed and stored X chunks.",
  "chunks": 1
}
```

### 3. Test Query Functionality
```powershell
curl -X POST "http://localhost:8000/api/query/" `
  -F "question=What is artificial intelligence?" `
  -F "mode=rag" `
  -F "top_k=3"
```

Expected response:
```json
{
  "status": "success",
  "final_answer": "...",
  "multi_llm_answers": [...],
  "retrieved_chunks": [...]
}
```

### 4. Access Frontend
Open: http://localhost:8501

Expected behavior:
- ChatGPT-style interface loads
- Sidebar navigation works
- Chat input accepts text

---

## 🐛 Troubleshooting

### Issue: Backend won't start
**Error**: `ModuleNotFoundError: No module named 'fastapi'`
**Solution**:
```powershell
pip install -r requirements.txt
```

### Issue: Frontend shows connection error
**Error**: "Cannot connect to backend"
**Solution**:
1. Check backend is running: http://localhost:8000/health
2. Verify CORS settings in `backend/main.py`
3. Check firewall isn't blocking ports 8000/8501

### Issue: Model loading fails
**Error**: "Error loading embedding model"
**Solution**:
```powershell
# Clear cache and reinstall
pip uninstall sentence-transformers -y
pip install sentence-transformers==2.2.2
```

### Issue: Import errors for new services
**Error**: `ImportError: cannot import name 'XXX'`
**Solution**:
```powershell
# Ensure all service files exist
ls services/*.py
# Should show all required service files
```

---

## 📊 Expected First Run Behavior

### Backend Startup (port 8000)
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Frontend Startup (port 8501)
```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### Model Loading (first time only)
```
INFO:services.embedder:Loading embedding model: all-MiniLM-L6-v2
Downloading: 100%|██████████| 123M/123M [00:45<00:00, 2.73MB/s]
INFO:services.embedder:Model loaded successfully. Embedding dimension: 384
```

---

## 🎯 Quick Usage Guide

### Upload a Document
1. Click **Data Management** in sidebar
2. Drag & drop a PDF/text file
3. Click **🚀 Process Documents**
4. Wait for "✅ X chunks indexed!" message

### Ask a Question
1. Return to **Chat** page
2. Type your question in the input box
3. Press Enter
4. View:
   - Individual model responses (cards)
   - Aggregated final answer
   - Retrieved context chunks (expandable)

### View Analytics
1. Click **Analytics** in sidebar
2. See:
   - Query metrics
   - Category distribution
   - Model performance

---

## 📝 Configuration Tips

### Adjust Chunk Size
Edit `pipelines/full_pipeline.py`:
```python
chunk_size = 512  # Default 512, increase for longer context
chunk_overlap = 50  # Default 50
```

### Change Vector Database
Set environment variable:
```powershell
$env:VECTOR_DB="chroma"  # or "faiss" (default)
```

### Increase Retrieval Results
Edit `frontend/components/chat_interface.py`:
```python
response = query_rag(user_query, mode="rag", top_k=10)  # Default is 5
```

---

## ✅ Success Indicators

You'll know everything is working when:
- ✅ Backend health check returns `{"status": "healthy"}`
- ✅ Frontend loads without errors
- ✅ You can upload a document successfully
- ✅ Query returns multi-model responses
- ✅ Chat history persists across sessions
- ✅ Analytics dashboard shows metrics

---

## 🚀 Next Steps

1. **Upload Your Data**: Add your PDFs, documents, or URLs
2. **Test Queries**: Ask domain-specific questions
3. **Tune Parameters**: Adjust chunk size, top_k, etc.
4. **Monitor Performance**: Check analytics for insights
5. **Customize UI**: Edit `frontend/styles.py` for branding

---

## 📞 Need Help?

- Check logs in terminal windows
- Review API docs: http://localhost:8000/docs
- Inspect browser console (F12) for frontend errors
- Verify all files exist: `ls -R`

**Happy RAG-ing! 🎉**
