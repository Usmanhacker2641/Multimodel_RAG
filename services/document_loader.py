from PyPDF2 import PdfReader
from docx import Document
import requests
from bs4 import BeautifulSoup
import easyocr
import whisper
import tempfile
import os
from pathlib import Path
from typing import Union, BinaryIO

class DocumentLoader:
    """
    Multi-format document loader that extracts text from various sources.
    Supports: PDF, DOCX, TXT, Images (OCR), Audio (Speech-to-Text), and URLs.
    """
    
    def __init__(self):
        self.ocr_reader = None
        self.whisper_model = None
    
    def load_document(self, source: Union[str, BinaryIO], source_type: str = None) -> str:
        """
        Main entry point to load any document type.
        
        Args:
            source: File path, URL, or file-like object
            source_type: Optional type hint ('pdf', 'docx', 'txt', 'image', 'audio', 'url')
        
        Returns:
            Extracted text as UTF-8 string
        """
        if source_type is None:
            source_type = self._detect_type(source)
        
        loaders = {
            'pdf': self.extract_from_pdf,
            'docx': self.extract_from_docx,
            'txt': self.extract_from_txt,
            'image': self.extract_from_image,
            'audio': self.extract_from_audio,
            'url': self.extract_from_url
        }
        
        loader = loaders.get(source_type)
        if not loader:
            raise ValueError(f"Unsupported source type: {source_type}")
        
        text = loader(source)
        return self._normalize_text(text)
    
    def _detect_type(self, source: Union[str, BinaryIO]) -> str:
        """Detect the type of source based on extension or content."""
        if isinstance(source, str):
            if source.startswith('http://') or source.startswith('https://'):
                return 'url'
            
            ext = Path(source).suffix.lower()
            type_map = {
                '.pdf': 'pdf',
                '.docx': 'docx',
                '.doc': 'docx',
                '.txt': 'txt',
                '.png': 'image',
                '.jpg': 'image',
                '.jpeg': 'image',
                '.bmp': 'image',
                '.tiff': 'image',
                '.mp3': 'audio',
                '.wav': 'audio',
                '.m4a': 'audio',
                '.flac': 'audio',
                '.ogg': 'audio'
            }
            return type_map.get(ext, 'txt')
        
        return 'pdf'  # Default for file objects
    
    def extract_from_pdf(self, file: Union[str, BinaryIO]) -> str:
        """Extract text from PDF file."""
        try:
            reader = PdfReader(file)
            text = " ".join(page.extract_text() or "" for page in reader.pages)
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting PDF: {str(e)}")
    
    def extract_from_docx(self, file: Union[str, BinaryIO]) -> str:
        """Extract text from DOCX file."""
        try:
            doc = Document(file)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return " ".join(paragraphs)
        except Exception as e:
            raise Exception(f"Error extracting DOCX: {str(e)}")
    
    def extract_from_txt(self, file: Union[str, BinaryIO]) -> str:
        """Extract text from TXT file."""
        try:
            if isinstance(file, str):
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            else:
                content = file.read()
                if isinstance(content, bytes):
                    return content.decode('utf-8', errors='ignore')
                return content
        except Exception as e:
            raise Exception(f"Error extracting TXT: {str(e)}")
    
    def extract_from_url(self, url: str) -> str:
        """Extract text from URL via web scraping."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            text = soup.get_text(separator=" ", strip=True)
            return text
        except Exception as e:
            raise Exception(f"Error extracting from URL: {str(e)}")
    
    def extract_from_image(self, file_path: str) -> str:
        """Extract text from image using OCR (EasyOCR)."""
        try:
            if self.ocr_reader is None:
                self.ocr_reader = easyocr.Reader(['en'], gpu=False)
            
            result = self.ocr_reader.readtext(file_path, detail=0, paragraph=True)
            return " ".join(result)
        except Exception as e:
            raise Exception(f"Error extracting from image: {str(e)}")
    
    def extract_from_audio(self, file_path: str) -> str:
        """Extract text from audio using Whisper speech-to-text."""
        try:
            if self.whisper_model is None:
                self.whisper_model = whisper.load_model("base")
            
            result = self.whisper_model.transcribe(file_path)
            return result["text"]
        except Exception as e:
            raise Exception(f"Error extracting from audio: {str(e)}")
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text to UTF-8 and clean whitespace."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = " ".join(text.split())
        
        # Ensure UTF-8 encoding
        if isinstance(text, bytes):
            text = text.decode('utf-8', errors='ignore')
        
        return text.strip()


# Convenience functions for backward compatibility
def extract_from_pdf(file):
    """Extract text from PDF file."""
    loader = DocumentLoader()
    return loader.extract_from_pdf(file)

def extract_from_docx(file):
    """Extract text from DOCX file."""
    loader = DocumentLoader()
    return loader.extract_from_docx(file)

def extract_from_url(url):
    """Extract text from URL."""
    loader = DocumentLoader()
    return loader.extract_from_url(url)

def extract_from_image(file_path):
    """Extract text from image using OCR."""
    loader = DocumentLoader()
    return loader.extract_from_image(file_path)

def extract_from_audio(file_path):
    """Extract text from audio using speech-to-text."""
    loader = DocumentLoader()
    return loader.extract_from_audio(file_path)