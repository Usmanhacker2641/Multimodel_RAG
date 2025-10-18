import streamlit as st
from pathlib import Path
import mimetypes
from datetime import datetime
from frontend.api_client import upload_text, upload_url, upload_file_bytes

def render_upload_panel():
    """
    Professional upload panel for File, Audio, Image, and URL uploads
    """
    st.markdown("""
        <style>
        .upload-container {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 1.5rem;
        }
        .upload-section {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            border-left: 4px solid #4A90E2;
        }
        .file-card {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            transition: all 0.3s ease;
        }
        .file-card:hover {
            box-shadow: 0 2px 8px rgba(74,144,226,0.2);
            border-color: #4A90E2;
        }
        .success-message {
            background: #d4edda;
            color: #155724;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #28a745;
            margin: 1rem 0;
        }
        .section-header {
            color: #2c3e50;
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("📤 Upload Panel")
    st.markdown("Upload your data sources for RAG-powered conversations")
    
    # Initialize session state
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    if 'uploaded_urls' not in st.session_state:
        st.session_state.uploaded_urls = []
    if 'processing_status' not in st.session_state:
        st.session_state.processing_status = {}
    
    # Document Upload Section
    with st.container():
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">📄 Document Upload</div>', unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "Upload PDF, Word, Text, or CSV files",
            type=['pdf', 'docx', 'txt', 'csv', 'xlsx', 'pptx'],
            accept_multiple_files=True,
            key="doc_uploader",
            help="Drag and drop files here or click to browse"
        )
        
        if uploaded_files:
            if st.button("🚀 Process Documents", key="process_docs"):
                process_files(uploaded_files, "document")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Image Upload Section
    with st.container():
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">🖼️ Image Upload</div>', unsafe_allow_html=True)
        
        uploaded_images = st.file_uploader(
            "Upload images for visual analysis",
            type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'],
            accept_multiple_files=True,
            key="image_uploader",
            help="Support for PNG, JPG, GIF, and more"
        )
        
        if uploaded_images:
            if st.button("🚀 Process Images", key="process_images"):
                process_files(uploaded_images, "image")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Audio Upload Section
    with st.container():
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">🔊 Audio Upload</div>', unsafe_allow_html=True)
        
        uploaded_audio = st.file_uploader(
            "Upload audio files",
            type=['mp3', 'wav', 'ogg', 'm4a', 'flac'],
            accept_multiple_files=True,
            key="audio_uploader",
            help="Upload audio files for transcription"
        )
        
        if uploaded_audio:
            if st.button("🚀 Process Audio", key="process_audio"):
                process_files(uploaded_audio, "audio")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # URL Fetch Section
    with st.container():
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">🌐 URL Fetch</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            url_input = st.text_input(
                "Enter URL to fetch content",
                placeholder="https://example.com/article",
                key="url_input",
                help="Enter a valid URL to crawl and extract content"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            fetch_button = st.button("🔍 Fetch", type="primary", use_container_width=True)
        
        if fetch_button and url_input:
            if url_input.startswith(('http://', 'https://')):
                with st.spinner("Fetching and processing content..."):
                    result = upload_url(url_input, metadata={"source": "url", "timestamp": datetime.now().isoformat()})
                    
                    if result.get("status") == "success":
                        st.session_state.uploaded_urls.append({
                            'url': url_input,
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'chunks': result.get("chunks", 0)
                        })
                        st.success(f"✅ Content fetched and {result.get('chunks', 0)} chunks indexed!")
                    else:
                        st.error(f"❌ {result.get('message', 'Failed to process URL')}")
            else:
                st.error("❌ Please enter a valid URL starting with http:// or https://")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display Processing Status
    if st.session_state.processing_status:
        st.markdown("---")
        st.markdown("### � Processing Status")
        for filename, status in st.session_state.processing_status.items():
            if status["status"] == "success":
                st.success(f"✅ {filename}: {status['chunks']} chunks indexed")
            else:
                st.error(f"❌ {filename}: {status.get('message', 'Failed')}")
    
    # Display Uploaded Content
    if st.session_state.uploaded_urls:
        st.markdown("---")
        st.markdown("### 📋 Successfully Processed URLs")
        
        for idx, url_data in enumerate(st.session_state.uploaded_urls):
            col1, col2, col3 = st.columns([0.5, 3, 1])
            
            with col1:
                st.markdown("<h3 style='margin:0'>🌐</h3>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"**{url_data['url']}**")
                st.caption(f"Processed: {url_data['timestamp']} • {url_data.get('chunks', 0)} chunks")
            with col3:
                if st.button("🗑️", key=f"del_url_{idx}"):
                    st.session_state.uploaded_urls.pop(idx)
                    st.rerun()


def process_files(files, file_type: str):
    """Process uploaded files through the backend API."""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, file in enumerate(files):
        status_text.text(f"Processing {file.name}...")
        
        try:
            result = upload_file_bytes(
                file.read(),
                file.name,
                metadata={"source": file_type, "timestamp": datetime.now().isoformat()}
            )
            
            if result.get("status") == "success":
                st.session_state.processing_status[file.name] = {
                    "status": "success",
                    "chunks": result.get("chunks", 0)
                }
            else:
                st.session_state.processing_status[file.name] = {
                    "status": "error",
                    "message": result.get("message", "Unknown error")
                }
        
        except Exception as e:
            st.session_state.processing_status[file.name] = {
                "status": "error",
                "message": str(e)
            }
        
        progress_bar.progress((idx + 1) / len(files))
    
    status_text.text("Processing complete!")
    progress_bar.empty()


def get_file_icon(filename):
    """Return appropriate icon based on file extension"""
    ext = Path(filename).suffix.lower()
    
    icon_map = {
        '.pdf': '📄',
        '.docx': '📝',
        '.doc': '📝',
        '.txt': '📃',
        '.csv': '📊',
        '.xlsx': '📊',
        '.xls': '📊',
        '.pptx': '📊',
        '.png': '🖼️',
        '.jpg': '🖼️',
        '.jpeg': '🖼️',
        '.gif': '🖼️',
        '.bmp': '🖼️',
        '.webp': '🖼️',
        '.mp3': '🔊',
        '.wav': '🔊',
        '.ogg': '🔊',
        '.m4a': '🔊',
        '.flac': '🔊',
    }
    
    return icon_map.get(ext, '📎')


if __name__ == "__main__":
    st.set_page_config(
        page_title="Upload Panel",
        page_icon="📤",
        layout="wide"
    )
    render_upload_panel()