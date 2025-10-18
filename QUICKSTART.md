# 🚀 Quick Start Guide - Multi-LLM RAG System

## ✅ Your System is Ready!

All components are connected and working:
- ✅ **Frontend UI** - Upload, Chat, Settings pages
- ✅ **Backend API** - FastAPI with all routes
- ✅ **Multi-LLM Support** - HuggingFace, DeepSeek, Gemini
- ✅ **Multimodal Upload** - Documents, Images, Audio, URLs
- ✅ **Vector Database** - FAISS/Chroma for semantic search
- ✅ **ASR/OCR Models** - Audio and image processing

---

## 🎯 How to Start

### 1. Launch the Application

```bash
python run.py
```

This will start:
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:8501

### 2. Open Your Browser

Go to: **http://localhost:8501**

---

## 📋 Step-by-Step Usage

### Step 1: Configure API Keys (First Time)

1. Click **⚙️ Settings & API Keys** in the sidebar
2. Enter your API keys:
   - **HuggingFace**: https://huggingface.co/settings/tokens
   - **DeepSeek**: https://platform.deepseek.com
   - **Gemini**: https://makersuite.google.com/app/apikey
3. Click **Save Settings**

> **Note**: Without API keys, the system will use stub responses for testing.

### Step 2: Upload Your Data

1. Click **📤 Upload** in the sidebar
2. Choose what to upload:

   **📄 Documents** (PDF, DOCX, TXT, CSV)
   - Drag and drop files
   - Click **🚀 Process Documents**

   **🖼️ Images** (PNG, JPG, GIF)
   - Upload images with text
   - Click **🚀 Process Images** (OCR will extract text)

   **🔊 Audio** (MP3, WAV, OGG)
   - Upload audio files
   - Click **🚀 Process Audio** (ASR will transcribe)

   **🌐 Web URL**
   - Enter URL (e.g., https://example.com/article)
   - Click **🔍 Fetch**

3. Wait for processing to complete
4. Check the success message with chunk count

### Step 3: Start Chatting

1. Click **💬 Chat** in the sidebar
2. Select models in the sidebar:
   - ✅ Mistral 7B (HuggingFace)
   - ✅ DeepSeek Chat
   - ✅ Gemini Pro
   - ⬜ Other models...

3. Type your question in the chat input
4. Press Enter

5. **You'll see**:
   - 🔍 System searches your uploaded documents
   - 🤖 All selected models generate responses in parallel
   - 📊 Individual model responses displayed
   - ✨ Final aggregated answer at the top

---

## 🎨 UI Features

### Sidebar Controls

**Active Models**: Enable/disable specific LLMs
- Mistral 7B, Falcon 7B, Zephyr 7B (HuggingFace)
- DeepSeek Chat, DeepSeek Coder
- Gemini Pro, Gemini Pro Vision

**Quick Settings**:
- **Top K Chunks**: How many relevant chunks to retrieve (1-20)
- **Mode**: RAG Mode (with context) or Direct Mode (no context)

**API Status**: Shows which API keys are configured
- ✅ = Key configured
- ❌ = Key missing

### Chat Interface

- **Clean ChatGPT-style UI**
- Message history preserved
- Real-time processing indicators
- Multi-model response cards with:
  - Model name
  - Response time
  - Token count
  - Confidence score

### Upload Panel

- **Multi-type support**: Documents, images, audio, URLs
- **Drag-and-drop** for files
- **Progress indicators** during processing
- **Success notifications** with chunk counts
- **Error handling** with clear messages

### Settings Page

- **API Key Management**: Secure password fields
- **Model Parameters**: Temperature, max tokens
- **RAG Settings**: Chunk size, overlap
- **Save functionality**: Persist settings

---

## 📊 Example Use Cases

### 1. Document Analysis
```
Upload: company_report.pdf
Ask: "What were the key financial highlights in Q4?"
→ System retrieves relevant sections
→ Multiple LLMs analyze and respond
→ Get comprehensive, multi-perspective answer
```

### 2. Research Assistant
```
Upload: Multiple research papers (PDF)
Ask: "What are the main findings about AI safety?"
→ Searches across all papers
→ Synthesizes insights from multiple sources
→ Provides well-rounded summary
```

### 3. Image Analysis
```
Upload: chart.png, diagram.jpg
Ask: "Explain the trends shown in these images"
→ OCR extracts text from images
→ Analyzes visual information
→ Provides detailed interpretation
```

### 4. Audio Transcription
```
Upload: meeting_recording.mp3
Ask: "What were the action items from the meeting?"
→ ASR transcribes audio
→ Identifies key points
→ Lists action items
```

### 5. Web Research
```
Upload URL: https://example.com/article
Ask: "Summarize the main arguments"
→ Scrapes and indexes article
→ Extracts key points
→ Provides structured summary
```

---

## ⚡ Quick Tips

1. **Model Selection**: 
   - Enable 2-3 models for balanced speed/diversity
   - More models = more perspectives but slower

2. **Upload Strategy**:
   - Upload related documents together
   - Use descriptive filenames
   - Process in batches for better organization

3. **Query Optimization**:
   - Be specific in your questions
   - Reference uploaded content when possible
   - Use natural language (no special syntax needed)

4. **Performance**:
   - Top K = 5-10 is usually optimal
   - Higher chunk size = more context but slower
   - Check API status before querying

---

## 🔧 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill the process if needed
taskkill /PID <process_id> /F

# Restart
python run.py
```

### Frontend won't load
- Ensure backend is running on port 8000
- Check browser console for errors
- Try clearing browser cache

### No responses from LLMs
- Verify API keys are entered correctly
- Check API key status in sidebar
- Review model selection (at least one enabled)
- Check backend logs for errors

### Upload fails
- Verify file size < 50MB
- Check file format is supported
- Ensure sufficient disk space
- Review backend logs

---

## 📚 Documentation

- **USER_GUIDE.md** - Comprehensive user manual
- **ARCHITECTURE.md** - System architecture and connections
- **README.md** - Project overview
- **STARTUP.md** - Detailed startup instructions

---

## 🎉 You're All Set!

Your Multi-LLM RAG system is ready to use. Here's what to do now:

1. ✅ **Run** `python run.py`
2. ✅ **Open** http://localhost:8501
3. ✅ **Add** your API keys
4. ✅ **Upload** some documents
5. ✅ **Start** asking questions!

Enjoy your powerful AI research assistant! 🚀

---

## 💡 Need Help?

- Check the **USER_GUIDE.md** for detailed instructions
- Review **ARCHITECTURE.md** to understand how components connect
- Check backend logs at http://localhost:8000/docs for API documentation
- Look for error messages in the UI for specific issues

**Happy RAGing! 🎊**
