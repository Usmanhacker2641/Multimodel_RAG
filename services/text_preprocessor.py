import re
from typing import List, Set
import hashlib

# text_preprocessor.py


def clean_text(text: str) -> str:
    """
    Cleans text by removing extra whitespace, HTML tags, and special characters.
    
    Args:
        text: Input text string to clean
        
    Returns:
        Cleaned text string
    """
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    
    # Remove special characters (keep alphanumeric, common punctuation, and spaces)
    text = re.sub(r'[^A-Za-z0-9.,!?\s]+', '', text)
    
    # Replace multiple whitespaces with single space
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def deduplicate_sentences(text: str) -> str:
    """
    Removes duplicate sentences from text using hash-based comparison.
    
    Args:
        text: Input text with potential duplicate sentences
        
    Returns:
        Text with duplicates removed
    """
    if not text:
        return ""
    
    seen: Set[str] = set()
    result: List[str] = []
    
    # Split by period and process each sentence
    sentences = text.split('.')
    
    for sentence in sentences:
        sent = sentence.strip()
        if sent and sent not in seen:
            seen.add(sent)
            result.append(sent)
    
    return '. '.join(result) + ('.' if result else '')


def normalize_case(text: str, lowercase: bool = True) -> str:
    """
    Normalizes text case.
    
    Args:
        text: Input text string
        lowercase: If True, converts to lowercase; otherwise uppercase
        
    Returns:
        Normalized text
    """
    if not text:
        return ""
    
    return text.lower() if lowercase else text.upper()


def remove_extra_spaces(text: str) -> str:
    """
    Removes leading, trailing, and redundant spaces.
    
    Args:
        text: Input text string
        
    Returns:
        Text with normalized spacing
    """
    return ' '.join(text.split())


def preprocess_text(text: str, lowercase: bool = False, deduplicate: bool = True) -> str:
    """
    Complete text preprocessing pipeline.
    
    Args:
        text: Raw input text
        lowercase: Whether to convert text to lowercase
        deduplicate: Whether to remove duplicate sentences
        
    Returns:
        Fully preprocessed text
    """
    if not text:
        return ""
    
    # Step 1: Clean text (remove HTML, special chars, extra whitespace)
    cleaned = clean_text(text)
    
    # Step 2: Deduplicate sentences if requested
    if deduplicate:
        cleaned = deduplicate_sentences(cleaned)
    
    # Step 3: Normalize case if requested
    if lowercase:
        cleaned = normalize_case(cleaned, lowercase=True)
    
    # Step 4: Final whitespace normalization
    cleaned = remove_extra_spaces(cleaned)
    
    return cleaned


class TextPreprocessor:
    """Wrapper class providing configurable text preprocessing."""

    def __init__(self, lowercase: bool = True, deduplicate: bool = True):
        self.lowercase = lowercase
        self.deduplicate = deduplicate

    def configure(self, *, lowercase: bool = None, deduplicate: bool = None) -> None:
        """Update preprocessing configuration at runtime."""
        if lowercase is not None:
            self.lowercase = lowercase
        if deduplicate is not None:
            self.deduplicate = deduplicate

    def preprocess(self, text: str) -> str:
        """Run the default preprocessing pipeline with current settings."""
        return preprocess_text(text, lowercase=self.lowercase, deduplicate=self.deduplicate)


if __name__ == "__main__":
    # Example usage
    sample_text = """
    <p>Hello World!  This is a test.  This is a test.</p>
    Hello World!  Special chars: @#$%^&*
    Extra    spaces   everywhere.
    """
    
    print("Original Text:")
    print(sample_text)
    print("\n" + "="*50 + "\n")
    
    processed = preprocess_text(sample_text, lowercase=True, deduplicate=True)
    print("Processed Text:")
    print(processed)