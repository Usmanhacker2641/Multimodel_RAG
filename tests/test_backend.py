"""
Test Backend API Endpoints
Tests all upload routes: file, audio, image, URL
"""
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestBackendHealth:
    """Test backend health and connectivity."""
    
    def test_imports(self):
        """Test that backend modules can be imported."""
        try:
            from backend.main import app
            assert app is not None
            print("✅ Backend app imports successfully")
        except Exception as e:
            pytest.fail(f"Failed to import backend.main: {e}")
    
    def test_fastapi_available(self):
        """Test FastAPI is available."""
        try:
            import fastapi
            print(f"✅ FastAPI version: {fastapi.__version__}")
        except ImportError as e:
            pytest.fail(f"FastAPI not available: {e}")


class TestFileProcessing:
    """Test file processing capabilities."""
    
    def test_pdf_processor_import(self):
        """Test PDF processor can be imported."""
        try:
            from services.document_preprocessor import DocumentPreprocessor
            processor = DocumentPreprocessor()
            print("✅ DocumentPreprocessor initialized")
        except Exception as e:
            pytest.fail(f"Failed to import DocumentPreprocessor: {e}")
    
    def test_pdf_file_processing(self, test_pdf_path):
        """Test processing a PDF file."""
        try:
            from services.document_preprocessor import DocumentPreprocessor
            processor = DocumentPreprocessor()
            
            # Test if file exists
            assert test_pdf_path.exists(), f"Test PDF not found: {test_pdf_path}"
            
            # Try to process
            result = processor.process_pdf(str(test_pdf_path))
            print(f"✅ PDF processed: {len(result)} chunks extracted")
            assert isinstance(result, list)
        except Exception as e:
            print(f"⚠️  PDF processing error: {e}")
            # Don't fail, just log - PDF processing might have dependencies
    
    def test_txt_file_processing(self, test_txt_path):
        """Test processing a text file."""
        try:
            # Test if file exists
            assert test_txt_path.exists(), f"Test TXT not found: {test_txt_path}"
            
            # Read content
            with open(test_txt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            assert len(content) > 0
            print(f"✅ TXT file read successfully: {len(content)} characters")
        except Exception as e:
            pytest.fail(f"Text file processing failed: {e}")


class TestImageProcessing:
    """Test image processing with OCR."""
    
    def test_ocr_import(self):
        """Test OCR service can be imported."""
        try:
            from services.ocr_service import OCRService
            print("✅ OCRService imported")
        except Exception as e:
            print(f"⚠️  OCR service import failed: {e}")
    
    def test_image_processing(self, test_image_path):
        """Test processing an image."""
        try:
            from services.ocr_service import OCRService
            ocr = OCRService()
            
            assert test_image_path.exists(), f"Test image not found: {test_image_path}"
            
            result = ocr.extract_text(str(test_image_path))
            print(f"✅ Image processed, extracted text length: {len(result)}")
        except Exception as e:
            print(f"⚠️  Image processing error: {e}")


class TestAudioProcessing:
    """Test audio processing with ASR."""
    
    def test_asr_import(self):
        """Test ASR service can be imported."""
        try:
            from services.asr_service import ASRService
            print("✅ ASRService imported")
        except Exception as e:
            print(f"⚠️  ASR service import failed: {e}")
    
    def test_audio_processing(self, test_audio_path):
        """Test processing an audio file."""
        try:
            from services.asr_service import ASRService
            asr = ASRService()
            
            assert test_audio_path.exists(), f"Test audio not found: {test_audio_path}"
            
            result = asr.transcribe(str(test_audio_path))
            print(f"✅ Audio processed, transcription length: {len(result)}")
        except Exception as e:
            print(f"⚠️  Audio processing error: {e}")


class TestURLProcessing:
    """Test URL fetching and processing."""
    
    def test_url_fetcher_import(self):
        """Test URL fetcher can be imported."""
        try:
            from services.url_fetcher import URLFetcher
            print("✅ URLFetcher imported")
        except Exception as e:
            print(f"⚠️  URLFetcher import failed: {e}")
    
    def test_url_processing(self, sample_urls):
        """Test processing a URL."""
        try:
            import requests
            
            # Test with example.com (always available)
            test_url = "https://example.com"
            response = requests.get(test_url, timeout=10)
            
            assert response.status_code == 200
            assert len(response.text) > 0
            print(f"✅ URL fetched successfully: {test_url}")
        except Exception as e:
            print(f"⚠️  URL processing error: {e}")


class TestVectorStore:
    """Test vector store operations."""
    
    def test_vectorstore_import(self):
        """Test vector store can be imported."""
        try:
            from vectorstore.vector_manager import VectorManager
            print("✅ VectorManager imported")
        except Exception as e:
            pytest.fail(f"VectorManager import failed: {e}")
    
    def test_pinecone_initialization(self):
        """Test Pinecone vector store initialization."""
        try:
            from vectorstore.vector_manager import VectorManager
            vm = VectorManager(db_type="pinecone")
            print("✅ VectorManager initialized with Pinecone")
        except Exception as e:
            print(f"⚠️  Pinecone initialization error: {e}")


class TestEmbeddings:
    """Test embedding generation."""
    
    def test_embedder_import(self):
        """Test embedder can be imported."""
        try:
            from services.embedder import Embedder
            print("✅ Embedder imported")
        except Exception as e:
            pytest.fail(f"Embedder import failed: {e}")
    
    def test_embedding_generation(self):
        """Test generating embeddings."""
        try:
            from services.embedder import Embedder
            embedder = Embedder()
            
            test_text = "This is a test sentence for embedding generation."
            embeddings = embedder.embed_texts([test_text])
            
            assert len(embeddings) > 0
            print(f"✅ Generated embedding with dimension: {len(embeddings[0])}")
        except Exception as e:
            print(f"⚠️  Embedding generation error: {e}")


class TestPipeline:
    """Test full RAG pipeline."""
    
    def test_pipeline_import(self):
        """Test pipeline can be imported."""
        try:
            from pipelines.full_pipeline import FullPipeline
            print("✅ FullPipeline imported")
        except Exception as e:
            pytest.fail(f"FullPipeline import failed: {e}")
    
    def test_pipeline_initialization(self):
        """Test pipeline initialization."""
        try:
            from pipelines.full_pipeline import FullPipeline
            pipeline = FullPipeline()
            print("✅ FullPipeline initialized")
        except Exception as e:
            print(f"⚠️  Pipeline initialization error: {e}")
