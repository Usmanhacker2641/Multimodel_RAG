"""
Text cleaning and preprocessing service.
Removes noise, normalizes whitespace, and prepares text for embedding.
"""
import re
from typing import Optional


def clean_text(text: str) -> str:
    """
    Clean and normalize text content.
    
    Args:
        text: Raw text to clean
    
    Returns:
        Cleaned and normalized text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?;:()\-\']', '', text)
    
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def normalize_whitespace(text: str) -> str:
    """Normalize all whitespace to single spaces."""
    return re.sub(r'\s+', ' ', text).strip()


def remove_urls(text: str) -> str:
    """Remove URLs from text."""
    return re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)


def remove_emails(text: str) -> str:
    """Remove email addresses from text."""
    return re.sub(r'\S+@\S+', '', text)
