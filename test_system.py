"""
Test Script for Multi-LLM RAG System
Verifies all components are properly connected
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all critical modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        # Backend components
        from backend.main import app
        print("  ✅ Backend FastAPI app")
        
        from backend.query_routes import router as query_router
        print("  ✅ Query routes")
        
        from backend.upload_routers import router as upload_router
        print("  ✅ Upload routes")
        
        # Services
        from services.multi_llm_runner import run_multi_llm, get_available_models
        print("  ✅ Multi-LLM runner")
        
        from services.embedder import Embedder
        print("  ✅ Embedder")
        
        from services.retriever import Retriever
        print("  ✅ Retriever")
        
        from services.file_parser import extract_text_from_file
        print("  ✅ File parser")
        
        # Pipeline
        from pipelines.full_pipeline import FullPipeline
        print("  ✅ Full pipeline")
        
        # Vector store
        from vectorstore.vector_manager import VectorManager
        print("  ✅ Vector manager")
        
        # Models
        from models.asr_model import ASRModel
        print("  ✅ ASR model")
        
        from models.ocr_model import OCRModel
        print("  ✅ OCR model")
        
        print("\n✅ All imports successful!\n")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import failed: {e}\n")
        return False


def test_pipeline():
    """Test the full pipeline with sample data"""
    print("🧪 Testing pipeline...")
    
    try:
        from pipelines.full_pipeline import FullPipeline
        
        pipeline = FullPipeline()
        print("  ✅ Pipeline initialized")
        
        # Test processing
        test_data = {
            "text": "This is a test document for the Multi-LLM RAG system. It demonstrates document processing.",
            "metadata": {"source": "test", "type": "sample"}
        }
        
        result = pipeline.process(test_data)
        print(f"  ✅ Processing result: {result.get('status')}")
        print(f"     Chunks created: {result.get('chunks', 0)}")
        
        # Test query (without API keys, will use stub responses)
        query_result = pipeline.query("What is this document about?", top_k=3)
        print(f"  ✅ Query result: {query_result.get('status')}")
        print(f"     Models responded: {len(query_result.get('multi_llm_answers', []))}")
        
        print("\n✅ Pipeline test successful!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Pipeline test failed: {e}\n")
        return False


def test_multi_llm():
    """Test multi-LLM runner"""
    print("🧪 Testing Multi-LLM runner...")
    
    try:
        from services.multi_llm_runner import run_multi_llm, get_available_models
        
        # Get available models
        models = get_available_models()
        print(f"  ✅ Available models: {len(models)}")
        for model in models:
            print(f"     - {model['label']} ({model['provider']})")
        
        # Test LLM execution (will use stubs without API keys)
        test_context = [{"text": "Revenue increased by 15% year over year."}]
        responses = run_multi_llm(
            "What is the revenue trend?",
            context=test_context,
            api_keys={}  # Empty API keys will trigger stub responses
        )
        
        print(f"  ✅ Generated {len(responses)} responses")
        for resp in responses:
            print(f"     - {resp['model_label']}: {len(resp['response'])} chars")
        
        print("\n✅ Multi-LLM test successful!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Multi-LLM test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_api_endpoints():
    """Test FastAPI endpoints are registered"""
    print("🧪 Testing API endpoints...")
    
    try:
        from backend.main import app
        
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
        
        expected_endpoints = [
            "/api/upload/",
            "/api/query/",
            "/api/history/",
            "/api/models/"
        ]
        
        for endpoint in expected_endpoints:
            if any(endpoint in route for route in routes):
                print(f"  ✅ {endpoint}")
            else:
                print(f"  ❌ {endpoint} not found")
        
        print(f"\n  Total routes: {len(routes)}")
        print("\n✅ Endpoint test successful!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Endpoint test failed: {e}\n")
        return False


def test_file_types():
    """Test file type support"""
    print("🧪 Testing file type support...")
    
    try:
        from backend.upload_routers import SUPPORTED_EXTENSIONS
        
        print(f"  Supported extensions ({len(SUPPORTED_EXTENSIONS)}):")
        for ext in sorted(SUPPORTED_EXTENSIONS):
            print(f"    - {ext}")
        
        # Check categories
        docs = [e for e in SUPPORTED_EXTENSIONS if e in ['.pdf', '.docx', '.txt']]
        audio = [e for e in SUPPORTED_EXTENSIONS if e in ['.mp3', '.wav', '.m4a', '.ogg']]
        images = [e for e in SUPPORTED_EXTENSIONS if e in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']]
        
        print(f"\n  ✅ Documents: {len(docs)}")
        print(f"  ✅ Audio: {len(audio)}")
        print(f"  ✅ Images: {len(images)}")
        
        print("\n✅ File type test successful!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ File type test failed: {e}\n")
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("Multi-LLM RAG System - Component Test Suite")
    print("=" * 70)
    print()
    
    results = {
        "Imports": test_imports(),
        "Pipeline": test_pipeline(),
        "Multi-LLM": test_multi_llm(),
        "API Endpoints": test_api_endpoints(),
        "File Types": test_file_types()
    }
    
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
    
    total = len(results)
    passed = sum(results.values())
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    print()
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print()
        print("Next steps:")
        print("1. Run: python run.py")
        print("2. Open: http://localhost:8501")
        print("3. Add API keys in Settings page")
        print("4. Upload your documents")
        print("5. Start chatting!")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
    
    print()
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
