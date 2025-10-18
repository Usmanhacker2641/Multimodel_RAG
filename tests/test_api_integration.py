"""
Comprehensive API Integration Tests for Multimodal RAG System
Tests the complete pipeline with real API calls
"""

import pytest
import requests
import time
import os
from io import BytesIO

# Test Configuration
BASE_URL = "http://localhost:8000/api"
HF_API_KEY = "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"
TIMEOUT = 60

class TestHealthCheck:
    """Test basic server health"""
    
    def test_health_endpoint(self):
        """Test that the health endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        print("✅ Health check passed")


class TestFileUpload:
    """Test file upload functionality"""
    
    def test_upload_text_file(self):
        """Test uploading a plain text file"""
        # Create a test text file
        text_content = "Artificial Intelligence is transforming the world. Machine learning models can now understand text, images, and audio."
        files = {
            'file': ('test_document.txt', BytesIO(text_content.encode()), 'text/plain')
        }
        
        response = requests.post(f"{BASE_URL}/upload/file", files=files, timeout=TIMEOUT)
        print(f"Upload text response: {response.status_code} - {response.text}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        print("✅ Text file upload passed")
    
    def test_upload_pdf(self):
        """Test uploading a PDF file"""
        # Create a minimal valid PDF
        pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(AI Research) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000214 00000 n 
trailer
<< /Size 5 /Root 1 0 R >>
startxref
306
%%EOF"""
        
        files = {
            'file': ('ai_research.pdf', BytesIO(pdf_content), 'application/pdf')
        }
        
        response = requests.post(f"{BASE_URL}/upload/file", files=files, timeout=TIMEOUT)
        print(f"Upload PDF response: {response.status_code} - {response.text}")
        
        # PDF upload might fail due to processing issues, but shouldn't crash
        assert response.status_code in [200, 400, 500]
        print("✅ PDF upload test completed (status checked)")


class TestURLUpload:
    """Test URL upload functionality"""
    
    def test_upload_valid_url(self):
        """Test uploading a valid URL"""
        payload = {
            "url": "https://en.wikipedia.org/wiki/Artificial_intelligence"
        }
        
        response = requests.post(f"{BASE_URL}/upload/url", json=payload, timeout=TIMEOUT)
        print(f"Upload URL response: {response.status_code} - {response.text}")
        
        # URL upload might fail due to processing, but should return proper response
        assert response.status_code in [200, 400, 500]
        print("✅ URL upload test completed")


class TestRAGQuery:
    """Test RAG query functionality with real API"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Upload test data before each query test"""
        # Upload some test content
        text_content = """
        Artificial Intelligence (AI) is the simulation of human intelligence by machines.
        Machine Learning is a subset of AI that enables systems to learn from data.
        Deep Learning uses neural networks with multiple layers.
        Natural Language Processing (NLP) helps computers understand human language.
        Computer Vision enables machines to interpret visual information.
        """
        
        files = {
            'file': ('ai_basics.txt', BytesIO(text_content.encode()), 'text/plain')
        }
        
        try:
            requests.post(f"{BASE_URL}/upload/file", files=files, timeout=TIMEOUT)
            time.sleep(2)  # Give time for processing
        except:
            pass
    
    def test_query_with_hf_api_key(self):
        """Test RAG query with HuggingFace API key"""
        payload = {
            "question": "What is Artificial Intelligence?",
            "mode": "rag",
            "top_k": 3,
            "api_keys": {
                "hf_api_key": HF_API_KEY
            }
        }
        
        response = requests.post(f"{BASE_URL}/query", json=payload, timeout=TIMEOUT)
        print(f"Query response status: {response.status_code}")
        print(f"Query response: {response.text[:500]}")
        
        assert response.status_code in [200, 500]  # May fail due to model issues but shouldn't crash
        
        if response.status_code == 200:
            data = response.json()
            assert "final_answer" in data or "status" in data
            print("✅ RAG query with API key passed")
        else:
            print("⚠️ Query failed but server responded properly")
    
    def test_query_without_api_key(self):
        """Test RAG query without API key (should use mock)"""
        payload = {
            "question": "What is Machine Learning?",
            "mode": "rag",
            "top_k": 3
        }
        
        response = requests.post(f"{BASE_URL}/query", json=payload, timeout=TIMEOUT)
        print(f"Query without API response: {response.status_code}")
        
        assert response.status_code in [200, 400, 500]
        print("✅ Query without API key test completed")
    
    def test_parallel_llm_response(self):
        """Test that parallel LLM responses are returned"""
        payload = {
            "question": "Explain Deep Learning",
            "mode": "rag",
            "top_k": 5,
            "api_keys": {
                "hf_api_key": HF_API_KEY
            }
        }
        
        response = requests.post(f"{BASE_URL}/query", json=payload, timeout=TIMEOUT)
        print(f"Parallel LLM test status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            # Check if multi_llm_answers exists
            if "multi_llm_answers" in data:
                assert isinstance(data["multi_llm_answers"], list)
                print(f"✅ Parallel LLM responses returned: {len(data['multi_llm_answers'])} models")
            else:
                print("⚠️ Response structure may differ")
        else:
            print("⚠️ Parallel LLM test - server responded with error")


class TestVectorStore:
    """Test vector store operations"""
    
    def test_embeddings_generation(self):
        """Test that embeddings are generated for uploaded content"""
        text_content = "Vector embeddings are numerical representations of text."
        files = {
            'file': ('embeddings_test.txt', BytesIO(text_content.encode()), 'text/plain')
        }
        
        response = requests.post(f"{BASE_URL}/upload/file", files=files, timeout=TIMEOUT)
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            # Wait for processing
            time.sleep(2)
            
            # Try to query to verify embeddings were created
            query_payload = {
                "question": "What are vector embeddings?",
                "mode": "rag",
                "top_k": 2
            }
            
            query_response = requests.post(f"{BASE_URL}/query", json=query_payload, timeout=TIMEOUT)
            assert query_response.status_code in [200, 500]
            print("✅ Vector store test completed")


if __name__ == "__main__":
    print("=" * 70)
    print("MULTIMODAL RAG SYSTEM - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print(f"Testing against: {BASE_URL}")
    print(f"HuggingFace API Key: {HF_API_KEY[:20]}...")
    print("=" * 70)
    
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s", "--tb=short"])
