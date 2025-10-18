"""
Comprehensive Test Suite for Multimodal RAG System
Tests file uploads (PDF, TXT, DOCX), audio, images, and URL processing
"""
import pytest
import os
import sys
from pathlib import Path
from io import BytesIO
from PIL import Image
import numpy as np

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "test_data"
TEST_DATA_DIR.mkdir(exist_ok=True)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment and create test files."""
    print("\n🔧 Setting up test environment...")
    
    # Create test PDF
    create_test_pdf()
    
    # Create test text file
    create_test_txt()
    
    # Create test image
    create_test_image()
    
    # Create test audio (simulated WAV file)
    create_test_audio()
    
    print("✅ Test environment ready\n")
    yield
    
    # Cleanup
    print("\n🧹 Cleaning up test files...")


def create_test_pdf():
    """Create a simple test PDF file."""
    pdf_path = TEST_DATA_DIR / "test_document.pdf"
    
    # Minimal valid PDF content
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(Test PDF Document) Tj
ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000262 00000 n 
0000000355 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
436
%%EOF
"""
    
    with open(pdf_path, "wb") as f:
        f.write(pdf_content)
    
    print(f"✅ Created test PDF: {pdf_path}")
    return pdf_path


def create_test_txt():
    """Create a test text file."""
    txt_path = TEST_DATA_DIR / "test_document.txt"
    
    content = """
    Artificial Intelligence and Machine Learning
    
    Artificial intelligence (AI) is intelligence demonstrated by machines, 
    in contrast to the natural intelligence displayed by humans and animals. 
    Leading AI textbooks define the field as the study of "intelligent agents": 
    any device that perceives its environment and takes actions that maximize 
    its chance of successfully achieving its goals.
    
    Machine learning (ML) is a field of inquiry devoted to understanding and 
    building methods that 'learn', that is, methods that leverage data to 
    improve performance on some set of tasks. It is seen as a part of 
    artificial intelligence.
    """
    
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"✅ Created test TXT: {txt_path}")
    return txt_path


def create_test_image():
    """Create a test image with text."""
    img_path = TEST_DATA_DIR / "test_image.png"
    
    # Create a simple image with text using PIL
    img = Image.new('RGB', (400, 200), color='white')
    
    # Note: PIL doesn't have built-in text rendering without ImageDraw and a font
    # For testing purposes, we'll create a simple colored image
    pixels = np.array(img)
    pixels[50:150, 50:350] = [0, 0, 255]  # Blue rectangle
    img = Image.fromarray(pixels.astype('uint8'))
    
    img.save(img_path)
    print(f"✅ Created test image: {img_path}")
    return img_path


def create_test_audio():
    """Create a test audio file (WAV format)."""
    audio_path = TEST_DATA_DIR / "test_audio.wav"
    
    # Create a minimal WAV file header
    # This is a simplified WAV file for testing purposes
    sample_rate = 16000
    duration = 1  # 1 second
    num_samples = sample_rate * duration
    
    # Generate a simple sine wave
    frequency = 440  # A4 note
    t = np.linspace(0, duration, num_samples)
    audio_data = np.sin(2 * np.pi * frequency * t)
    
    # Convert to 16-bit PCM
    audio_data = (audio_data * 32767).astype(np.int16)
    
    # Write WAV file
    import wave
    with wave.open(str(audio_path), 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    print(f"✅ Created test audio: {audio_path}")
    return audio_path


# Test fixtures
@pytest.fixture
def test_pdf_path():
    """Return path to test PDF."""
    return TEST_DATA_DIR / "test_document.pdf"


@pytest.fixture
def test_txt_path():
    """Return path to test TXT."""
    return TEST_DATA_DIR / "test_document.txt"


@pytest.fixture
def test_image_path():
    """Return path to test image."""
    return TEST_DATA_DIR / "test_image.png"


@pytest.fixture
def test_audio_path():
    """Return path to test audio."""
    return TEST_DATA_DIR / "test_audio.wav"


@pytest.fixture
def sample_urls():
    """Return sample URLs for testing."""
    return [
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://www.python.org/",
        "https://example.com"
    ]
