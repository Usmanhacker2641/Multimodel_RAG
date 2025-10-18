
import pytest
from fastapi.testclient import TestClient
from backend.main import app  # Assuming your FastAPI app is in backend/main.py
import os
from unittest.mock import patch, MagicMock

# Create a TestClient for the FastAPI app
client = TestClient(app)

# Create a dummy PDF file for testing
DUMMY_PDF_CONTENT = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /MediaBox [0 0 612 792] >>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000059 00000 n \n0000000112 00000 n \ntrailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n178\n%%EOF"
DUMMY_PDF_PATH = "tests/dummy.pdf"

# Create a dummy text file for testing
DUMMY_TXT_CONTENT = "This is a test text file."
DUMMY_TXT_PATH = "tests/dummy.txt"

@pytest.fixture(scope="session", autouse=True)
def create_dummy_files():
    """Create dummy files for testing."""
    os.makedirs("tests", exist_ok=True)
    with open(DUMMY_PDF_PATH, "wb") as f:
        f.write(DUMMY_PDF_CONTENT)
    with open(DUMMY_TXT_PATH, "w") as f:
        f.write(DUMMY_TXT_CONTENT)
    yield
    # Teardown: remove dummy files
    os.remove(DUMMY_PDF_PATH)
    os.remove(DUMMY_TXT_PATH)

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch('services.document_preprocessor.process_pdf')
def test_upload_pdf(mock_process_pdf):
    """Test uploading a PDF file."""
    mock_process_pdf.return_value = [("This is a test page.", {})]
    with open(DUMMY_PDF_PATH, "rb") as f:
        response = client.post("/api/upload/file", files={"file": ("dummy.pdf", f, "application/pdf")})
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "dummy.pdf" in response.json()["message"]
    mock_process_pdf.assert_called_once()

def test_upload_txt():
    """Test uploading a text file."""
    with open(DUMMY_TXT_PATH, "rb") as f:
        response = client.post("/api/upload/file", files={"file": ("dummy.txt", f, "text/plain")})
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "dummy.txt" in response.json()["message"]

@patch('requests.get')
def test_upload_url_success(mock_get):
    """Test uploading a URL successfully."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body>This is a test page.</body></html>"
    mock_get.return_value = mock_response

    response = client.post("/api/upload/url", json={"url": "http://example.com"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "http://example.com" in response.json()["message"]
    mock_get.assert_called_once_with("http://example.com", timeout=30)

def test_upload_url_failure():
    """Test uploading a URL that fails to fetch."""
    response = client.post("/api/upload/url", json={"url": "http://invalid-url-that-does-not-exist.com"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Failed to fetch URL: http://invalid-url-that-does-not-exist.com"
