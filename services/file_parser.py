"""
File parser service for extracting text from various file formats.
Supports PDF, DOCX, TXT, audio files, and images with OCR.
"""
from typing import Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_text_from_file(file_path: str, file_type: str) -> str:
    """
    Extract text content from uploaded files.
    
    Args:
        file_path: Path to the file
        file_type: Type of file (pdf, docx, txt, audio, image)
    
    Returns:
        Extracted text content
    """
    try:
        file_ext = Path(file_path).suffix.lower()
        
        # Text files
        if file_ext in ['.txt']:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        # PDF files
        elif file_ext == '.pdf':
            try:
                import PyPDF2
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = []
                    for page in reader.pages:
                        text.append(page.extract_text())
                    return '\n'.join(text)
            except ImportError:
                logger.warning("PyPDF2 not installed. Install with: pip install PyPDF2")
                return ""
        
        # DOCX files
        elif file_ext in ['.docx', '.doc']:
            try:
                import docx
                doc = docx.Document(file_path)
                text = [para.text for para in doc.paragraphs]
                return '\n'.join(text)
            except ImportError:
                logger.warning("python-docx not installed. Install with: pip install python-docx")
                return ""
        
        # Audio files (using Whisper or similar)
        elif file_ext in ['.mp3', '.wav', '.m4a', '.ogg']:
            try:
                from models.asr_model import ASRModel
                asr = ASRModel()
                return asr.transcribe(file_path)
            except Exception as e:
                logger.warning(f"Audio transcription failed: {e}")
                return f"[Audio file: {Path(file_path).name}]"
        
        # Image files (using OCR)
        elif file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']:
            try:
                from models.ocr_model import OCRModel
                ocr = OCRModel()
                return ocr.extract_text(file_path)
            except Exception as e:
                logger.warning(f"OCR extraction failed: {e}")
                return f"[Image file: {Path(file_path).name}]"
        
        else:
            logger.warning(f"Unsupported file type: {file_ext}")
            return ""
    
    except Exception as e:
        logger.error(f"Error extracting text from {file_path}: {e}")
        return ""
